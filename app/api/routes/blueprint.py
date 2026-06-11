from fastapi import APIRouter, Header, HTTPException, Request

from app.models.schemas import BlueprintRequest, BlueprintResponse
from app.services.blueprint_generator import BlueprintGenerator, BlueprintParseError
from app.services.llm.base import LLMProviderError

router = APIRouter()


@router.post("/generate-blueprint", response_model=BlueprintResponse)
async def generate_blueprint(
    request: Request,
    body: BlueprintRequest,
    x_llm_provider: str | None = Header(default=None, alias="X-LLM-Provider"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> BlueprintResponse:
    if x_llm_provider in ("anthropic", "openai"):
        if not x_api_key:
            raise HTTPException(
                status_code=400,
                detail=f"X-API-Key header is required when X-LLM-Provider is '{x_llm_provider}'.",
            )
        try:
            if x_llm_provider == "anthropic":
                from app.services.llm.anthropic import AnthropicLLMProvider
                provider = AnthropicLLMProvider(api_key=x_api_key)
            else:
                from app.services.llm.openai_provider import OpenAILLMProvider
                provider = OpenAILLMProvider(api_key=x_api_key)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        provider = request.app.state.provider

    generator = BlueprintGenerator(provider)
    try:
        output = await generator.generate(body)
        return BlueprintResponse(success=True, data=output)
    except LLMProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except BlueprintParseError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc
