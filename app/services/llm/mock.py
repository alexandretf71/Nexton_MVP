import json
from pathlib import Path

from app.services.llm.base import LLMProvider

_FIXTURE_PATH = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "mock_blueprint.json"


class MockLLMProvider(LLMProvider):
    """Deterministic provider for tests and offline development.

    Returns a hard-coded fixture regardless of prompt content so the full
    pipeline can be exercised without any network calls or API keys.
    """

    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        return _FIXTURE_PATH.read_text(encoding="utf-8")

    @property
    def provider_name(self) -> str:
        return "mock"
