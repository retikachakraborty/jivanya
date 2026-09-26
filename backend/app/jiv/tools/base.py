from abc import ABC, abstractmethod
from typing import Any, Optional, Type

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.jiv.schemas.chat import UserProfileSchema


class BaseTool(ABC):
    """Abstract base class for all Jiv backend execution tools."""

    name: str
    description: str
    args_schema: Type[BaseModel]

    @abstractmethod
    def execute(
        self,
        db: Session,
        user_profile: Optional[UserProfileSchema] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute the tool against deterministic database / API capabilities."""
        pass

    def get_schema(self) -> dict[str, Any]:
        """Return OpenAI / Gemini compatible tool declaration schema."""
        json_schema = self.args_schema.model_json_schema()
        properties = json_schema.get("properties", {})
        required = json_schema.get("required", [])

        # Clean schema for LLM function declaration
        cleaned_properties: dict[str, Any] = {}
        for prop_name, prop_data in properties.items():
            # Handle Pydantic v2 Optional[T] which produces anyOf: [{...}, {type: 'null'}]
            target = prop_data
            if "anyOf" in prop_data:
                non_null = [v for v in prop_data["anyOf"] if v.get("type") != "null"]
                if non_null:
                    target = non_null[0]

            prop_type = target.get("type", "string")
            cleaned_prop: dict[str, Any] = {
                "type": prop_type,
                "description": prop_data.get("description") or target.get("description", ""),
            }
            if "items" in target:
                cleaned_prop["items"] = target["items"]
            elif "items" in prop_data:
                cleaned_prop["items"] = prop_data["items"]
            if "enum" in target:
                cleaned_prop["enum"] = target["enum"]
            elif "enum" in prop_data:
                cleaned_prop["enum"] = prop_data["enum"]

            cleaned_properties[prop_name] = cleaned_prop

        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": cleaned_properties,
                "required": required,
            },
        }
