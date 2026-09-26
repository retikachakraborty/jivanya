from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.jiv.agent.orchestrator import jiv_agent
from app.jiv.providers.factory import get_llm_provider
from app.jiv.schemas.chat import JivChatRequest, JivChatResponse
from app.jiv.tools.registry import tool_registry

router = APIRouter(prefix="/api/v1/jiv", tags=["Jiv Conversational Agent"])


@router.post("/chat", response_model=JivChatResponse)
def chat_with_jiv(
    request: JivChatRequest,
    db: Session = Depends(get_db),
) -> JivChatResponse:
    """
    Main Jiv conversational intelligence endpoint.
    Orchestrates natural language requests through verified tools,
    enforcing deterministic safety, profile constraints, and context persistence.
    """
    return jiv_agent.process(db=db, request=request)


@router.get("/tools")
def list_jiv_tools() -> list[dict[str, Any]]:
    """List all registered Jiv tools and their JSON schemas."""
    return tool_registry.get_schemas()


@router.get("/status")
def jiv_status() -> dict[str, Any]:
    """Check Jiv agent status and active provider."""
    provider = get_llm_provider()
    return {
        "status": "online",
        "agent": "Jiv",
        "provider": provider.__class__.__name__,
        "tools_count": len(tool_registry.list_tools()),
        "voice_stt": "server-side Groq Whisper transcription",
    }
