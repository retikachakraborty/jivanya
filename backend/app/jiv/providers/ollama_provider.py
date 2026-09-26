import json
import os
from typing import Any, Optional

import requests

from app.jiv.providers.base import BaseLLMProvider, LLMResponse, ToolCall
from app.jiv.schemas.chat import ChatMessage


class OllamaProvider(BaseLLMProvider):
    """
    Ollama / OpenAI-compatible provider for local model execution (Qwen2.5, Llama3, etc.).
    Configurable via LLM_BASE_URL (defaults to http://localhost:11434/v1).
    """

    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None) -> None:
        self.base_url = base_url or os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        self.model = model or os.getenv("LLM_MODEL", "qwen2.5:7b")
        self.api_key = os.getenv("LLM_API_KEY", "ollama")

    def chat(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        system_instruction: str,
        temperature: float = 0.2,
    ) -> LLMResponse:
        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"

        openai_messages = [{"role": "system", "content": system_instruction}]
        for msg in messages:
            item: dict[str, Any] = {"role": msg.role, "content": msg.content or ""}
            if msg.role == "tool":
                item["tool_call_id"] = msg.tool_call_id or "call_0"
            if msg.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": tc.get("id", "call_0"),
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc.get("arguments", {})),
                        },
                    }
                    for tc in msg.tool_calls
                ]
            openai_messages.append(item)

        openai_tools = []
        if tools:
            for t in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": t.get("parameters", {}),
                    },
                })

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
        }
        if openai_tools:
            payload["tools"] = openai_tools

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        resp = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})

        tool_calls: list[ToolCall] = []
        for tc in msg.get("tool_calls", []):
            fn = tc.get("function", {})
            try:
                args = json.loads(fn.get("arguments", "{}"))
            except Exception:
                args = {}
            tool_calls.append(ToolCall(name=fn.get("name", ""), arguments=args, id=tc.get("id")))

        return LLMResponse(
            text=msg.get("content"),
            tool_calls=tool_calls,
            raw_response=data,
        )
