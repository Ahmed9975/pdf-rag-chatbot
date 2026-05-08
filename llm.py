from __future__ import annotations

from ollama import ChatResponse, chat

from config import MODEL_NAME


class LLMServiceError(RuntimeError):
    """Raised when the local LLM call fails."""


def strip_thinking_blocks(text: str) -> str:
    if "</think>" not in text:
        return text.strip()
    return text.split("</think>")[-1].strip()


def get_response(prompt: str, model_name: str = MODEL_NAME) -> str:
    """Send a prompt to Ollama and return the final visible answer."""
    try:
        response: ChatResponse = chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:  # pragma: no cover
        raise LLMServiceError(f"Failed to get a response from Ollama: {exc}") from exc

    text = response.message.content or ""
    return strip_thinking_blocks(text)
