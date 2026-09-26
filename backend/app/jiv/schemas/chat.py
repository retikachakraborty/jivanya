from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class UserProfileSchema(BaseModel):
    diet_preference: Optional[str] = Field(default="no preference", alias="dietPreference")
    allergies: list[str] = Field(default_factory=list)
    exclusions: list[str] = Field(default_factory=list)
    no_onion: bool = Field(default=False, alias="noOnion")
    no_garlic: bool = Field(default=False, alias="noGarlic")
    cuisine_preferences: list[str] = Field(default_factory=list, alias="cuisinePreferences")

    model_config = {"populate_by_name": True}

    @field_validator("allergies", "exclusions", "cuisine_preferences", mode="before")
    @classmethod
    def normalize_lists(cls, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return sorted({str(item).strip().lower() for item in value if str(item).strip()})

    @field_validator("no_onion", "no_garlic", mode="before")
    @classmethod
    def normalize_flags(cls, value: Any) -> bool:
        if isinstance(value, str):
            return value.strip().lower() == "true"
        return value is True or value == 1

    @field_validator("diet_preference", mode="before")
    @classmethod
    def normalize_diet(cls, value: Any) -> str:
        normalized = str(value or "no preference").strip().lower()
        return normalized if normalized in {"vegetarian", "vegan", "diabetic friendly", "no preference"} else "no preference"


class VisionContextSchema(BaseModel):
    label: str
    confidence: float
    canonical_name: Optional[str] = None
    model_name: str = "vegetables"
    confirmed: bool = False
    is_restricted: bool = False


class ChatMessage(BaseModel):
    role: str = Field(description="Role of the message sender: 'user', 'assistant', 'system', or 'tool'")
    content: Optional[str] = None
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[list[dict[str, Any]]] = None


class JivChatRequest(BaseModel):
    message: str = Field(description="User natural-language request")
    session_id: Optional[str] = Field(default=None, description="Identifier for conversation state tracking")
    profile: Optional[UserProfileSchema] = Field(default=None, description="Saved user profile constraints")
    vision_context: Optional[VisionContextSchema] = Field(default=None, description="Optional vision detection context")


class JivChatResponse(BaseModel):
    reply: str
    session_id: str
    tool_called: Optional[str] = None
    tool_result: Optional[dict[str, Any]] = None
    sources: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    conversation_state: Optional[dict[str, Any]] = None
