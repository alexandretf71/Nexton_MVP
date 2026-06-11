import openai as openai_sdk

from app.core.config import settings
from app.services.llm.base import LLMProvider, LLMProviderError


class OpenAILLMProvider(LLMProvider):
    def __init__(self, api_key: str | None = None) -> None:
        resolved_key = api_key or settings.OPENAI_API_KEY
        if not resolved_key:
            raise ValueError(
                "No OpenAI API key available. Set OPENAI_API_KEY in .env "
                "or provide it in the UI settings panel."
            )
        self._client = openai_sdk.AsyncOpenAI(api_key=resolved_key)

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=settings.OPENAI_MODEL_ID,
                response_format={"type": "json_object"},
                temperature=0.2,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=4096,
            )
        except openai_sdk.OpenAIError as exc:
            raise LLMProviderError(f"OpenAI request failed: {exc}") from exc

        content = response.choices[0].message.content
        if content is None:
            raise LLMProviderError("OpenAI returned an empty response.")
        return content

    @property
    def provider_name(self) -> str:
        return "openai"
