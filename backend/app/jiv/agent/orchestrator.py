import json
import re
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.jiv.context.manager import context_manager
from app.jiv.providers.factory import get_llm_provider
from app.jiv.safety.hallucination_guard import HallucinationGuard
from app.jiv.safety.restriction_guard import RestrictionGuard
from app.jiv.schemas.chat import (
    ChatMessage,
    JivChatRequest,
    JivChatResponse,
)
from app.jiv.tools.registry import tool_registry
from app.jiv.providers.base import LLMResponse, ToolCall

SYSTEM_INSTRUCTION = (
    "You are Jiv, the food intelligence companion for Jivanya in India. "
    "You help users cook with what they have, find recipes, check packaged foods, "
    "explore verified IFCT 2017 nutrition compositions, and respect personal dietary boundaries.\n"
    "Rules:\n"
    "1. The existing Jivanya backend database and algorithms are your sole source of truth.\n"
    "2. NEVER fabricate or guess nutritional numbers, prices, ingredients, recipes, or medical safety.\n"
    "3. User profile restrictions (allergies, exclusions, no onion, no garlic, diet) are non-negotiable hard constraints.\n"
    "4. When the user asks what to cook or make with ingredients (e.g., 'what can I make with chicken and lentils', 'recipes with paneer and spinach', 'I have eggs'), you MUST call match_recipes with available_ingredients containing those items.\n"
    "5. When the user asks for a dish name, course, or cuisine (e.g., 'biryani', 'dal tadka', 'breakfast'), call search_recipes with query, course, or cuisine.\n"
    "6. NEVER call search_recipes or match_recipes with empty {} arguments when ingredients or dishes were mentioned in the query.\n"
    "7. Always explain verified results clearly and concisely."
)


class JivAgent:
    """Core Jiv Conversational Agent and Tool Orchestrator."""

    def __init__(self) -> None:
        self.registry = tool_registry

    @staticmethod
    def _deterministic_intent(message: str, state: Any) -> Optional[ToolCall]:
        """Turn recipe language into structured concepts before any verbalization."""
        text = message.lower().strip()
        nutrition = re.search(
            r"(?:nutrition(?:al)?(?:\s+(?:values?|info|breakdown))?\s+(?:of|for)\s+|calories\s+in\s+|ifct\s+code\s+)([a-z0-9][a-z0-9 -]*)$",
            text,
        ) or re.search(r"^([a-z][a-z -]+?)\s+nutrition(?:\s+(?:values?|info|breakdown))?$", text)
        if nutrition:
            value = nutrition.group(1).strip()
            return ToolCall(name="lookup_nutrition", arguments={"ingredient_name": value})
        if "basket" in text or "grocery list" in text:
            return None

        count_match = re.search(r"\b(\d{1,3})\s+(?:(?:[a-z-]+)\s+){0,3}(?:recipes?|dishes?)\b", text)
        limit = min(max(int(count_match.group(1)), 1), 100) if count_match else 20
        cuisine_names = {
            "assamese": "Assamese", "bengali": "Bengali Recipes", "punjabi": "Punjabi",
            "south indian": "South Indian Recipes", "north indian": "North Indian Recipes",
            "gujarati": "Gujarati Recipes", "maharashtrian": "Maharashtrian Recipes",
            "rajasthani": "Rajasthani", "kerala": "Kerala", "chinese": ["Chinese", "Indo Chinese"],
        }
        cuisine = next((value for key, value in cuisine_names.items() if key in text), None)
        diet = "vegan" if "vegan" in text else "vegetarian" if re.search(r"\bvegetarian\b|\bveg\b", text) else None
        course_map = {
            "breakfast": ["South Indian Breakfast", "World Breakfast", "North Indian Breakfast", "Indian Breakfast"],
            "lunch": ["Lunch"], "dinner": ["Dinner"], "snack": ["Snack"],
            "brunch": ["Brunch"], "appetizer": ["Appetizer"], "dessert": ["Dessert"],
        }
        course_key = next((key for key in course_map if re.search(rf"\b{re.escape(key)}s?\b", text)), None)
        course = course_map.get(course_key) if course_key else None
        health_goal = "high_protein" if re.search(r"\bhigh[- ]protein\b", text) else "healthy" if re.search(r"\bhealthy\b|\bhealthier\b", text) else None
        explicit_max = re.search(r"(?:under|less than|within|in)\s+(\d+)\s*(?:min|mins|minute|minutes)", text)
        max_time = int(explicit_max.group(1)) if explicit_max else (30 if re.search(r"\b(?:quick|quickly|fast)\b", text) else None)
        excluded: list[str] = []
        without = re.search(r"(?:without|with no|no|exclude|excluding|leave out)\s+([^?.]+)", text)
        if without:
            excluded = [part.strip() for part in re.split(r"\s*(?:,|\band\b|&)\s*", without.group(1)) if part.strip()]
        include_match = re.search(r"\b(?:with|using|containing)\s+([^?.]+)", text)
        ingredients: list[str] = []
        if include_match:
            raw = re.sub(r"\b(?:for|a|an|some|tonight|today|please)\b", "", include_match.group(1))
            ingredients = [part.strip() for part in re.split(r"\s*(?:,|\band\b|&)\s*", raw) if part.strip()]
        explicit_recipe_target = re.search(r"(?:search|find)\s+recipes?\s+for\s+([^?.]+)", text)
        if explicit_recipe_target and not ingredients:
            target = explicit_recipe_target.group(1).strip()
            ingredients = [target]
        asks_recipe = bool(re.search(r"\brecipes?\b|\bsomething\b|\bwhat can i (?:have|cook|make)\b|\bsuggest\b|\bshow me\b", text))
        if (asks_recipe or course or cuisine or diet or ingredients or excluded or health_goal or max_time or count_match):
            args: dict[str, Any] = {"limit": limit}
            if cuisine: args["cuisine"] = cuisine
            if course: args["course"] = course
            if diet: args["diet"] = diet
            if ingredients: args["ingredients"] = ingredients
            if excluded: args["exclude"] = excluded
            if health_goal: args["health_goal"] = health_goal
            if max_time is not None: args["max_time"] = max_time
            return ToolCall(name="search_recipes", arguments=args)
        return None

    def process(self, db: Session, request: JivChatRequest) -> JivChatResponse:
        # 1. State extraction and session management
        state = context_manager.get_or_create(request.session_id)
        state = context_manager.extract_and_update(state, request.message, request.profile)

        warnings: list[str] = []
        is_allergy_related = bool(request.profile and (request.profile.allergies or request.profile.exclusions))
        has_vision = False

        # 2. Vision integration handoff
        if request.vision_context:
            has_vision = True
            vc = request.vision_context
            canonical_label = (vc.canonical_name or vc.label).strip()
            # Low confidence check (< 0.70)
            if vc.confidence < 0.70 and not vc.confirmed:
                return JivChatResponse(
                    reply=(
                        f"Vision recognition identified **{vc.label}** with {round(vc.confidence * 100)}% confidence. "
                        f"Because this is below our confidence threshold, please confirm if this is correct "
                        f"before I proceed with recipe search or nutrition checks."
                        + HallucinationGuard.VISION_DISCLAIMER
                    ),
                    session_id=state.session_id,
                    warnings=["Low-confidence vision detection needs user confirmation."],
                    conversation_state=state.to_dict(),
                )

            # Check restrictions on detected vision item
            res = RestrictionGuard.evaluate_ingredient(db, canonical_label, request.profile)
            if not res["allowed"]:
                return JivChatResponse(
                    reply=(
                        f"⚠️ The detected item **{canonical_label}** {res['reason']} "
                        f"Jiv cannot recommend recipes or foods containing this item."
                        + HallucinationGuard.VISION_DISCLAIMER
                    ),
                    session_id=state.session_id,
                    warnings=[str(res["reason"])],
                    conversation_state=state.to_dict(),
                )

            # High confidence or confirmed safe item -> add to active ingredients
            if canonical_label not in state.active_ingredients:
                state.active_ingredients.append(canonical_label)
            if canonical_label not in state.vision_items:
                state.vision_items.append(canonical_label)

        # 3. Formulate conversation messages
        messages = [
            ChatMessage(role="system", content=SYSTEM_INSTRUCTION),
            ChatMessage(role="user", content=request.message),
        ]

        # 4. Invoke LLM provider
        provider = get_llm_provider()
        tools_schemas = self.registry.get_schemas()

        try:
            forced_call = self._deterministic_intent(request.message, state)
            llm_response = LLMResponse(tool_calls=[forced_call]) if forced_call else provider.chat(
                messages=messages,
                tools=tools_schemas,
                system_instruction=SYSTEM_INSTRUCTION,
            )
        except Exception as exc:
            # Safe failure fallback
            return JivChatResponse(
                reply=f"I'm temporarily unable to reach the conversational engine ({exc}). Deterministic features remain online.",
                session_id=state.session_id,
                warnings=["LLM provider unavailable"],
                conversation_state=state.to_dict(),
            )

        tool_called: Optional[str] = None
        tool_result: Optional[dict[str, Any]] = None
        sources: list[dict[str, Any]] = []

        # 5. Handle tool call if requested by provider
        if llm_response.tool_calls:
            first_call = llm_response.tool_calls[0]
            tool_called = first_call.name
            tool_args = first_call.arguments.copy()

            # Parameter guard: If tool is search_recipes with no query and no ingredients,
            # but user has active ingredients or mentioned ingredients, reroute to match_recipes
            if tool_called == "search_recipes":
                has_filter = bool(
                    tool_args.get("query") or tool_args.get("ingredients") or tool_args.get("cuisine")
                    or tool_args.get("course") or tool_args.get("diet") or tool_args.get("exclude")
                    or tool_args.get("max_time") or tool_args.get("health_goal")
                )
                if not has_filter and state.active_ingredients:
                    tool_called = "match_recipes"
                    tool_args["available_ingredients"] = list(state.active_ingredients)

            elif tool_called == "match_recipes":
                if not tool_args.get("available_ingredients") and state.active_ingredients:
                    tool_args["available_ingredients"] = list(state.active_ingredients)

            # Incorporate state accumulated from previous turns if not explicitly supplied
            if tool_called in {"search_recipes", "match_recipes"}:
                if state.active_max_time and "max_time" not in tool_args:
                    tool_args["max_time"] = state.active_max_time
                if state.active_no_onion and "no_onion" not in tool_args:
                    tool_args["no_onion"] = True
                if state.active_no_garlic and "no_garlic" not in tool_args:
                    tool_args["no_garlic"] = True
                if state.active_diet and "diet" not in tool_args:
                    tool_args["diet"] = state.active_diet
                if state.last_offset and "offset" not in tool_args:
                    tool_args["offset"] = state.last_offset
                if state.active_cuisine and "cuisine" not in tool_args:
                    tool_args["cuisine"] = state.active_cuisine

            # Execute tool against verified backend
            tool_result = self.registry.execute(
                tool_name=tool_called,
                db=db,
                user_profile=request.profile,
                arguments=tool_args,
            )

            # Store in state
            state.last_tool_called = tool_called
            state.last_tool_result = tool_result
            context_manager.save(state)

            # Extract source items
            if isinstance(tool_result, dict):
                if "items" in tool_result:
                    sources = tool_result["items"]
                elif "selected_products" in tool_result:
                    sources = tool_result["selected_products"][:5]
                elif "matched_food" in tool_result and tool_result["matched_food"]:
                    sources = [tool_result["matched_food"]]

            # Pass tool results back to provider for natural conversational response
            messages.append(ChatMessage(
                role="assistant",
                content=None,
                tool_calls=[{"name": tool_called, "arguments": tool_args}],
            ))
            messages.append(ChatMessage(
                role="tool",
                name=tool_called,
                content=json.dumps(tool_result),
            ))

            try:
                final_response = provider.chat(
                    messages=messages,
                    tools=tools_schemas,
                    system_instruction=SYSTEM_INSTRUCTION,
                )
                raw_reply = final_response.text or "I processed your request using the verified Jivanya library."
            except Exception as exc:
                raw_reply = f"Retrieved verified data, but conversational formatting encountered an error: {exc}"
        else:
            raw_reply = llm_response.text or "How can I help you with recipes, nutrition, or food choices today?"

        # 6. Post-execution Safety and Guard Enforcement
        # Ensure LLM did not try to override hard restrictions
        blocked_items = []
        if request.profile:
            blocked_items.extend(request.profile.allergies)
            blocked_items.extend(request.profile.exclusions)

        safe_reply = RestrictionGuard.enforce_text_safety(raw_reply, blocked_items, request.profile)

        # Sanitize against hallucinations and add required medical/vision disclaimers
        final_reply = HallucinationGuard.sanitize_response(
            text=safe_reply,
            tool_called=tool_called,
            tool_result=tool_result,
            has_vision=has_vision,
            is_allergy_related=is_allergy_related,
        )

        return JivChatResponse(
            reply=final_reply,
            session_id=state.session_id,
            tool_called=tool_called,
            tool_result=tool_result,
            sources=sources,
            warnings=warnings,
            conversation_state=state.to_dict(),
        )


jiv_agent = JivAgent()
