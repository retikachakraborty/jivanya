from typing import Any, Optional


class HallucinationGuard:
    """Safeguards against fabricated facts, unsupported nutrition data, and unsafe medical claims."""

    MEDICAL_DISCLAIMER = (
        "\n\n*Note: Jivanya records your profile choices to filter recommendations. "
        "This is not medical advice or an allergy guarantee.*"
    )

    VISION_DISCLAIMER = (
        "\n\n*Note: Visual detection is not proof that a food is allergen-free, "
        "medically safe, or free of hidden ingredients or cross-contamination.*"
    )

    @classmethod
    def sanitize_response(
        cls,
        text: str,
        tool_called: Optional[str],
        tool_result: Optional[dict[str, Any]],
        has_vision: bool = False,
        is_allergy_related: bool = False,
    ) -> str:
        # 1. Check if tool returned empty results
        if tool_result:
            status = str(tool_result.get("status", "")).upper()
            if status == "BLOCKED_BY_ALLERGY":
                return text if "allerg" in text.lower() or "profile" in text.lower() else (
                    "I found matching records, but I won't recommend them because the requested ingredient "
                    "conflicts with an allergy saved in your Jivanya profile. I can help find alternatives."
                ) + cls.MEDICAL_DISCLAIMER
            if status == "BLOCKED_BY_DIETARY_RESTRICTION":
                return text if "restriction" in text.lower() or "profile" in text.lower() else (
                    "Matching records were blocked by your saved dietary restrictions, so I won't recommend them."
                )
            is_empty = False
            if tool_called in {"search_recipes", "match_recipes"}:
                items = tool_result.get("items", [])
                if not items:
                    is_empty = True
            elif tool_called == "lookup_nutrition":
                if not tool_result.get("matched_food"):
                    is_empty = True
            elif tool_called == "search_products":
                items = tool_result.get("items", [])
                if not items:
                    is_empty = True

            # If tool executed and returned 0 results, ensure text doesn't invent records
            if is_empty:
                if "no matching" not in text.lower() and "unavailable" not in text.lower() and "not found" not in text.lower():
                    text = (
                        "I searched the Jivanya verified database, but no matching records were found for your request. "
                        "I cannot generate or assume nutritional or recipe data that is not in our database."
                    )

        # 2. Append required safety disclaimers
        if has_vision and cls.VISION_DISCLAIMER.strip() not in text:
            text += cls.VISION_DISCLAIMER
        elif is_allergy_related and cls.MEDICAL_DISCLAIMER.strip() not in text:
            text += cls.MEDICAL_DISCLAIMER

        return text
