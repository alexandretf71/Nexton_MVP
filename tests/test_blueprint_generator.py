import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.models.schemas import BlueprintOutput, BlueprintRequest
from app.services.blueprint_generator import BlueprintGenerator, BlueprintParseError
from app.services.llm.mock import MockLLMProvider


@pytest.fixture
def generator(mock_provider):
    return BlueprintGenerator(mock_provider)


class TestMockLLMProvider:
    async def test_returns_string(self, mock_provider):
        result = await mock_provider.complete("system", "user")
        assert isinstance(result, str)

    async def test_returns_valid_json(self, mock_provider):
        result = await mock_provider.complete("system", "user")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    async def test_response_validates_as_blueprint_content(self, mock_provider):
        result = await mock_provider.complete("system", "user")
        data = json.loads(result)
        # Inject metadata to allow full model validation
        data["generated_at"] = datetime.now(timezone.utc)
        data["provider_used"] = "mock"
        BlueprintOutput.model_validate(data)

    def test_provider_name(self, mock_provider):
        assert mock_provider.provider_name == "mock"

    async def test_ignores_prompt_content(self, mock_provider):
        r1 = await mock_provider.complete("any system prompt", "any user prompt")
        r2 = await mock_provider.complete("different", "different")
        assert r1 == r2


class TestBlueprintGenerator:
    async def test_returns_blueprint_output(self, generator, sample_request):
        result = await generator.generate(sample_request)
        assert isinstance(result, BlueprintOutput)

    async def test_all_sections_populated(self, generator, sample_request):
        result = await generator.generate(sample_request)
        assert result.business_problem_summary
        assert result.operational_pain_points
        assert result.ai_opportunity_classification
        assert result.recommended_solution_type
        assert result.suggested_architecture
        assert result.agentic_workflow
        assert result.data_requirements
        assert result.integration_points
        assert result.engineering_backlog
        assert result.risks_and_assumptions
        assert result.testing_plan
        assert result.executive_summary
        assert result.delivery_status_report

    async def test_injects_provider_name(self, generator, sample_request):
        result = await generator.generate(sample_request)
        assert result.provider_used == "mock"

    async def test_injects_generated_at(self, generator, sample_request):
        before = datetime.now(timezone.utc)
        result = await generator.generate(sample_request)
        assert result.generated_at >= before

    async def test_mock_provider_sets_model_id_to_none(self, generator, sample_request):
        result = await generator.generate(sample_request)
        assert result.model_id is None

    async def test_invalid_json_raises_parse_error(self, sample_request):
        bad_provider = AsyncMock()
        bad_provider.complete = AsyncMock(return_value="not valid json {{")
        bad_provider.provider_name = "mock"
        generator = BlueprintGenerator(bad_provider)
        with pytest.raises(BlueprintParseError, match="invalid JSON"):
            await generator.generate(sample_request)

    async def test_schema_mismatch_raises_parse_error(self, sample_request):
        bad_provider = AsyncMock()
        bad_provider.complete = AsyncMock(return_value='{"wrong_field": "value"}')
        bad_provider.provider_name = "mock"
        generator = BlueprintGenerator(bad_provider)
        with pytest.raises(BlueprintParseError, match="schema validation"):
            await generator.generate(sample_request)
