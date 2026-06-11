from abc import ABC, abstractmethod


class LLMProviderError(Exception):
    """Raised when an LLM provider's API call fails (auth, quota, model access, network)."""


class LLMProvider(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompts to the LLM and return the raw JSON string response."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier returned in API responses."""
        ...
