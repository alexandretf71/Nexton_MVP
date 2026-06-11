import json
from datetime import datetime, timezone

from pydantic import ValidationError

from app.core.config import settings
from app.core.prompt_templates import SYSTEM_PROMPT, build_user_prompt
from app.models.schemas import BlueprintOutput, BlueprintRequest
from app.services.llm.base import LLMProvider


class BlueprintParseError(Exception):
    def __init__(self, message: str, raw_output: str = "") -> None:
        super().__init__(message)
        self.raw_output = raw_output


class BlueprintGenerator:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def generate(self, request: BlueprintRequest) -> BlueprintOutput:
        user_prompt = build_user_prompt(request)

        raw = await self.provider.complete(SYSTEM_PROMPT, user_prompt)

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise BlueprintParseError("LLM returned invalid JSON", raw_output=raw) from exc

        # Inject metadata — these fields are not produced by the LLM.
        data["generated_at"] = datetime.now(timezone.utc)
        data["provider_used"] = self.provider.provider_name
        data["model_id"] = settings.MODEL_ID if settings.LLM_PROVIDER != "mock" else None

        try:
            return BlueprintOutput.model_validate(data)
        except ValidationError as exc:
            raise BlueprintParseError(
                f"LLM response failed schema validation: {exc}",
                raw_output=str(data),
            ) from exc
