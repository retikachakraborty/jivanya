from typing import Any, Optional

from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.jiv.schemas.chat import UserProfileSchema
from app.jiv.tools.base import BaseTool
from app.jiv.tools.basket_tools import OptimizeBasketTool
from app.jiv.tools.explain_tools import ExplainResultTool
from app.jiv.tools.nutrition_tools import LookupNutritionTool
from app.jiv.tools.product_tools import CompareProductsTool, SearchProductsTool
from app.jiv.tools.recipe_tools import MatchRecipesTool, SearchRecipesTool
from app.jiv.tools.restriction_tools import CheckRestrictionsTool


class ToolRegistry:
    """Central registry and executor for Jiv tools."""

    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}
        self.register(SearchRecipesTool())
        self.register(MatchRecipesTool())
        self.register(LookupNutritionTool())
        self.register(SearchProductsTool())
        self.register(CompareProductsTool())
        self.register(CheckRestrictionsTool())
        self.register(OptimizeBasketTool())
        self.register(ExplainResultTool())

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_schemas(self) -> list[dict[str, Any]]:
        return [tool.get_schema() for tool in self._tools.values()]

    def execute(
        self,
        tool_name: str,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        arguments: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        tool = self.get(tool_name)
        if not tool:
            return {
                "error": f"Tool '{tool_name}' is not recognized.",
                "tool_called": tool_name,
                "status": "failed",
            }

        args = arguments or {}

        # Validate arguments using the tool's Pydantic schema
        try:
            validated = tool.args_schema.model_validate(args)
            validated_dict = validated.model_dump()
        except ValidationError as exc:
            return {
                "error": f"Invalid arguments for tool '{tool_name}': {exc.errors()}",
                "tool_called": tool_name,
                "status": "validation_error",
            }

        try:
            result = tool.execute(db=db, user_profile=user_profile, **validated_dict)
            return result
        except Exception as exc:
            return {
                "error": f"Backend execution error in tool '{tool_name}': {str(exc)}",
                "tool_called": tool_name,
                "status": "execution_error",
            }


tool_registry = ToolRegistry()
