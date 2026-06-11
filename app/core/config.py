from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    LLM_PROVIDER: str = "mock"
    ANTHROPIC_API_KEY: str = ""
    MODEL_ID: str = "claude-sonnet-4-6"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_ID: str = "gpt-4o"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = False

    UI_API_BASE_URL: str = "http://localhost:8000"
    UI_ORIGIN: str = "http://localhost:8502"
    APP_VERSION: str = "1.0.0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
