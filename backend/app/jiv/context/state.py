from typing import Any, Optional
from pydantic import BaseModel, Field


class ConversationState(BaseModel):
    session_id: str
    last_intent: Optional[str] = None
    active_query: Optional[str] = None
    active_ingredients: list[str] = Field(default_factory=list)
    active_cuisine: Optional[str] = None
    active_course: Optional[str] = None
    active_diet: Optional[str] = None
    active_max_time: Optional[int] = None
    active_no_onion: bool = False
    active_no_garlic: bool = False
    active_exclusions: list[str] = Field(default_factory=list)
    last_tool_called: Optional[str] = None
    last_tool_result: Optional[dict[str, Any]] = None
    last_offset: int = 0
    vision_items: list[str] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
