import anthropic

from app.core.config import settings
from app.services.llm.base import LLMProvider, LLMProviderError


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str | None = None) -> None:
        resolved_key = api_key or settings.ANTHROPIC_API_KEY
        if not resolved_key:
            raise ValueError(
                "No Anthropic API key available. Set ANTHROPIC_API_KEY in .env "
                "or provide it in the UI settings panel."
            )
        self._client = anthropic.AsyncAnthropic(api_key=resolved_key)

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            message = await self._client.messages.create(
                model=settings.MODEL_ID,
                max_tokens=4096,
                # Cache the system prompt — it is constant across all requests.
                system=[
                    {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
                ],
                messages=[{"role": "user", "content": user_prompt}],
            )
        except anthropic.AnthropicError as exc:
            raise LLMProviderError(f"Anthropic request failed: {exc}") from exc

        return message.content[0].text

    @property
    def provider_name(self) -> str:
        return "anthropic"
