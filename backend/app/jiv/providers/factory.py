import os
from typing import Optional

from app.jiv.providers.base import BaseLLMProvider
from app.jiv.providers.gemini_provider import GeminiProvider
from app.jiv.providers.mock_provider import MockLLMProvider
from app.jiv.providers.ollama_provider import OllamaProvider

_override_provider: Optional[BaseLLMProvider] = None


def get_llm_provider() -> BaseLLMProvider:
    """Resolve the active LLM provider based on configuration or override."""
    global _override_provider
    if _override_provider is not None:
        return _override_provider

    provider_name = os.getenv("LLM_PROVIDER", "").strip().lower()

    if provider_name == "gemini":
        return GeminiProvider()
    elif provider_name in {"ollama", "openai", "openai_compatible"}:
        return OllamaProvider()

    # Default to deterministic mock provider
    return MockLLMProvider()


def set_llm_provider(provider: Optional[BaseLLMProvider]) -> None:
    """Set or clear a provider override (useful for testing)."""
    global _override_provider
    _override_provider = provider
