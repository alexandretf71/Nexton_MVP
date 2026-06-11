from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import blueprint, health
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.LLM_PROVIDER == "anthropic":
        from app.services.llm.anthropic import AnthropicLLMProvider
        app.state.provider = AnthropicLLMProvider()
    elif settings.LLM_PROVIDER == "openai":
        from app.services.llm.openai_provider import OpenAILLMProvider
        app.state.provider = OpenAILLMProvider()
    else:
        from app.services.llm.mock import MockLLMProvider
        app.state.provider = MockLLMProvider()
    yield


app = FastAPI(
    title="AI Implementation Copilot",
    description="Transforms a messy business problem into a structured AI implementation blueprint.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.UI_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(blueprint.router)
