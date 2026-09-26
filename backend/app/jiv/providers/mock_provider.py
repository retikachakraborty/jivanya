import json
import re
from typing import Any

from app.jiv.providers.base import BaseLLMProvider, LLMResponse, ToolCall
from app.jiv.schemas.chat import ChatMessage


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic Mock LLM Provider.
    Extracts intents, emits validated structured tool calls, and synthesizes
    verified conversational responses from tool results without external dependencies.
    """

    def chat(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        system_instruction: str,
        temperature: float = 0.2,
    ) -> LLMResponse:
        last_message = messages[-1]

        # If last message is a tool response, summarize the tool results into natural language
        if last_message.role == "tool":
            return self._format_tool_response(messages)

        # Otherwise, determine which tool to call based on user input
        text = (last_message.content or "").lower().strip()

        # The count is an explicit user requirement and must survive tool selection.
        count_match = re.search(r"\b(\d{1,3})\s+(?:[a-z-]+\s+)?(?:recipes?|dishes?)\b", text)
        requested_limit = min(max(int(count_match.group(1)), 1), 100) if count_match else 20

        # 1. Product comparison
        compare_match = re.search(r"compare\s+(?:products?\s+)?([\d\s,]+)", text)
        if compare_match:
            barcodes = [int(b.strip()) for b in re.findall(r"\d+", compare_match.group(1))]
            if len(barcodes) >= 2:
                return LLMResponse(tool_calls=[ToolCall(name="compare_products", arguments={"product_ids": barcodes})])

        # 2. Check restrictions / Allergy inquiry
        restriction_match = re.search(
            r"(?:can i eat|is it safe to eat|check restrictions? for|allergy check for|allergic to)\s+([^?.]+)",
            text,
        )
        if restriction_match:
            raw_items = [i.strip() for i in re.split(r",|and", restriction_match.group(1)) if i.strip()]
            return LLMResponse(tool_calls=[ToolCall(name="check_restrictions", arguments={"ingredient_ids": raw_items})])

        # 3. Nutrition lookup
        nutrition_match = re.search(r"(?:nutrition(?:al)?(?:\s+(?:values?|info|breakdown))?\s+(?:of|for)\s+|calories\s+in\s+|ifct\s+code\s+)([a-zA-Z0-9][a-zA-Z0-9\s-]*)", text)
        if not nutrition_match:
            nutrition_match = re.search(r"^([a-zA-Z][a-zA-Z -]+?)\s+nutrition(?:\s+(?:values?|info|breakdown))?\s*$", text)
        if nutrition_match:
            item = nutrition_match.group(1).strip()
            if re.match(r"^[a-zA-Z]\d{3}$", item, re.I):
                return LLMResponse(tool_calls=[ToolCall(name="lookup_nutrition", arguments={"food_id": item})])
            return LLMResponse(tool_calls=[ToolCall(name="lookup_nutrition", arguments={"ingredient_name": item})])

        # 4. Packaged product search
        product_match = re.search(
            r"(?:packaged\s+foods?|products?|which\s+packaged\s+([a-zA-Z]+)|search\s+products?\s+([a-zA-Z]+)|find\s+packaged\s+([a-zA-Z]+))",
            text,
        )
        if product_match:
            term = next((g for g in product_match.groups() if g), "")
            query = term.strip() if term else None
            category = "oats" if "oat" in text else (query or None)
            return LLMResponse(tool_calls=[ToolCall(name="search_products", arguments={"category": category, "query": query})])

        # 5. Basket optimization
        if "basket" in text or "grocery list" in text:
            priority = "high_protein" if "protein" in text else "low_sugar" if "sugar" in text else "balanced"
            return LLMResponse(tool_calls=[ToolCall(name="optimize_basket", arguments={"priorities": [priority]})])

        # Extract common modifiers
        max_time = None
        time_match = re.search(r"(?:under|less than|within|in)\s+(\d+)\s*(?:min|mins|minute|minutes)", text)
        if time_match:
            max_time = int(time_match.group(1))

        no_onion = True if re.search(r"\b(?:no|without|remove)\s+onion\b", text) else None
        no_garlic = True if re.search(r"\b(?:no|without|remove)\s+garlic\b", text) else None
        diet = "vegetarian" if "vegetarian" in text or "veg" in text else "vegan" if "vegan" in text else None

        cuisine_values = {
            "assamese": "Assamese", "bengali": "Bengali", "punjabi": "Punjabi",
            "south indian": "South Indian Recipes", "north indian": "North Indian Recipes",
            "gujarati": "Gujarati", "maharashtrian": "Maharashtrian", "rajasthani": "Rajasthani",
        }
        cuisine = next((value for key, value in cuisine_values.items() if key in text), None)
        course = next((value for value in ("breakfast", "lunch", "dinner", "snack") if value in text), None)
        if cuisine or course:
            args = {"limit": requested_limit}
            if cuisine: args["cuisine"] = cuisine
            if course: args["course"] = course
            if diet: args["diet"] = diet
            return LLMResponse(tool_calls=[ToolCall(name="search_recipes", arguments=args)])

        # 6. Explicit Recipe search: "give me a recipe using X", "find a recipe for X", "recipe for X"
        recipe_search_match = re.search(
            r"(?:give\s+me\s+a\s+recipe\s+using|recipe\s+using|find\s+a\s+recipe\s+for|recipe\s+for|search\s+recipes?\s+for)\s+([^?.]+)",
            text,
        )
        if recipe_search_match:
            raw_target = recipe_search_match.group(1).replace("recipe", "").strip()
            args: dict[str, Any] = {"query": raw_target, "ingredients": [raw_target]}
            if max_time:
                args["max_time"] = max_time
            if no_onion is not None:
                args["no_onion"] = no_onion
            if no_garlic is not None:
                args["no_garlic"] = no_garlic
            if diet:
                args["diet"] = diet
            args["limit"] = requested_limit
            return LLMResponse(tool_calls=[ToolCall(name="search_recipes", arguments=args)])

        # 7. Recipe matching with on-hand ingredients ("cook with X", "make with X", "I have X", "recipes with X")
        from app.jiv.context.manager import context_manager
        extracted_ings = context_manager.extract_ingredients(text)
        if extracted_ings:
            match_args: dict[str, Any] = {"available_ingredients": extracted_ings}
            if max_time:
                match_args["max_time"] = max_time
            if no_onion is not None:
                match_args["no_onion"] = no_onion
            if no_garlic is not None:
                match_args["no_garlic"] = no_garlic
            if diet:
                match_args["diet"] = diet
            match_args["limit"] = requested_limit
            return LLMResponse(tool_calls=[ToolCall(name="match_recipes", arguments=match_args)])

        # 8. Explain result
        explain_match = re.search(r"why\s+(?:was|is)\s+(?:this\s+)?([a-zA-Z0-9_-]+)\s+(?:recommended|chosen|selected)", text)
        if explain_match:
            return LLMResponse(tool_calls=[ToolCall(name="explain_result", arguments={"result_id": explain_match.group(1)})])

        # 9. Default to recipe search
        fallback_args: dict[str, Any] = {}
        if max_time:
            fallback_args["max_time"] = max_time
        if no_onion is not None:
            fallback_args["no_onion"] = no_onion
        if no_garlic is not None:
            fallback_args["no_garlic"] = no_garlic
        if diet:
            fallback_args["diet"] = diet

        fallback_args["limit"] = requested_limit
        return LLMResponse(tool_calls=[ToolCall(name="search_recipes", arguments=fallback_args)])

    def _format_tool_response(self, messages: list[ChatMessage]) -> LLMResponse:
        tool_msg = messages[-1]
        try:
            data = json.loads(tool_msg.content or "{}")
        except Exception:
            return LLMResponse(text="I received an unformatted response from the backend service.")

        tool_name = tool_msg.name or ""

        # Recipe tools
        if tool_name in {"search_recipes", "match_recipes"}:
            items = data.get("items", [])
            ignored = data.get("ignored_ingredients", [])
            if not items:
                if data.get("status", "").startswith("BLOCKED_BY_"):
                    return LLMResponse(text=("I found matching recipe records, but they are blocked by your saved "
                        "allergy or dietary restrictions. I won't recommend them; I can help find alternatives."))
                msg = "I searched Jivanya's recipe library, but no recipes matched your criteria."
                if ignored:
                    msg += f" Note that the following ingredients were excluded due to your saved profile constraints: {', '.join(ignored)}."
                return LLMResponse(text=msg)

            lines = [f"I found {len(items)} recipe(s) matching your criteria:"]
            for idx, item in enumerate(items, 1):
                time_info = f" ({item.get('total_minutes')} mins)" if item.get("total_minutes") else ""
                cuisine = f" [{item.get('cuisine')}]" if item.get("cuisine") else ""
                lines.append(f"{idx}. **{item.get('recipe_name')}**{cuisine}{time_info}")
                if item.get("matched_ingredients"):
                    lines.append(f"   - Matched ingredients: {', '.join(item.get('matched_ingredients'))}")

            if ignored:
                lines.append(f"\n*Excluded ingredients per your profile:* {', '.join(ignored)}.")

            return LLMResponse(text="\n".join(lines))

        # Nutrition tool
        elif tool_name == "lookup_nutrition":
            food = data.get("matched_food")
            if not food:
                return LLMResponse(text=data.get("message", "Nutritional information is unavailable in the IFCT 2017 database."))
            return LLMResponse(
                text=(
                    f"**Verified IFCT 2017 Nutrition for {food.get('food_name')}** (per 100g):\n"
                    f"- Energy: {food.get('energy_kcal', 0)} kcal\n"
                    f"- Protein: {food.get('protein_g', 0)} g\n"
                    f"- Carbohydrates: {food.get('carbohydrate_g', 0)} g\n"
                    f"- Fat: {food.get('fat_g', 0)} g\n"
                    f"- Fiber: {food.get('fiber_g', 0)} g\n"
                    f"- Calcium: {food.get('calcium_mg', 0)} mg\n"
                    f"- Iron: {food.get('iron_mg', 0)} mg\n"
                    f"- Sodium: {food.get('sodium_mg', 0)} mg"
                )
            )

        # Product tools
        elif tool_name == "search_products":
            items = data.get("items", [])
            if not items:
                return LLMResponse(text="No packaged products found in the catalog matching your search.")
            lines = [f"Found {len(items)} product(s):"]
            for p in items[:3]:
                warning_note = f" ⚠️ *{p.get('warning')}*" if p.get("warning") else ""
                lines.append(
                    f"- **{p.get('product_name')}** ({p.get('brand') or 'General'}) — "
                    f"Protein: {p.get('protein_100g', 0)}g, Sugar: {p.get('sugars_100g', 0)}g per 100g.{warning_note}"
                )
            return LLMResponse(text="\n".join(lines))

        elif tool_name == "compare_products":
            items = data.get("items", [])
            if not items:
                return LLMResponse(text=data.get("error", "Unable to compare specified products."))
            lines = ["**Product Comparison:**"]
            for p in items:
                warning_note = f" ⚠️ *{p.get('warning')}*" if p.get("warning") else ""
                lines.append(
                    f"- **{p.get('product_name')}**: {p.get('protein_100g', 0)}g protein, "
                    f"{p.get('sugars_100g', 0)}g sugars, {p.get('sodium_100g', 0)}mg sodium per 100g.{warning_note}"
                )
            return LLMResponse(text="\n".join(lines))

        # Restriction check tool
        elif tool_name == "check_restrictions":
            status = data.get("overall_status")
            summary = data.get("summary", "")
            lines = [f"**Profile Restriction Check: {status}**\n{summary}"]
            for ing in data.get("ingredients", []):
                icon = "✓" if ing.get("allowed") else "✗"
                lines.append(f"- {icon} **{ing.get('ingredient')}**: {ing.get('reason')}")
            return LLMResponse(text="\n".join(lines))

        # Basket tool
        elif tool_name == "optimize_basket":
            items = data.get("selected_products", [])
            metrics = data.get("metrics_per_100g_sum", {})
            lines = [
                f"**Optimized Product Basket** ({data.get('summary')}):",
                f"- Total Protein (sum/100g): {metrics.get('total_protein_g', 0)}g",
                f"- Total Sugars (sum/100g): {metrics.get('total_sugars_g', 0)}g\n",
                "Selected items:",
            ]
            for p in items:
                lines.append(f"- **{p.get('product_name')}** ({p.get('brand') or 'General'})")
            return LLMResponse(text="\n".join(lines))

        # Explain result tool
        elif tool_name == "explain_result":
            return LLMResponse(text=f"**Explanation:** {data.get('explanation', 'Verified against deterministic ranking factors.')}")

        return LLMResponse(text=json.dumps(data))
