from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field

from app.jiv.schemas.chat import ChatMessage


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    id: Optional[str] = None


class LLMResponse(BaseModel):
    text: Optional[str] = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
    raw_response: Optional[dict[str, Any]] = None


class BaseLLMProvider(ABC):
    """Abstract interface for LLM providers (Mock, Gemini, Ollama, OpenAI-compatible)."""

    @abstractmethod
    def chat(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        system_instruction: str,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Process messages and return an LLMResponse (either tool calls or text reply)."""
        pass
