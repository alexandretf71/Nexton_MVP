from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.prompt_templates import SYSTEM_PROMPT
from app.models.schemas import BlueprintRequest, SolutionType

_REQUIRED_OUTPUT_FIELDS = [
    "business_problem_summary",
    "operational_pain_points",
    "ai_opportunity_classification",
    "recommended_solution_type",
    "suggested_architecture",
    "agentic_workflow",
    "data_requirements",
    "integration_points",
    "engineering_backlog",
    "risks_and_assumptions",
    "testing_plan",
    "executive_summary",
    "delivery_status_report",
    "delivery_team",
]


class TestBlueprintRequest:
    def test_valid_minimum(self):
        req = BlueprintRequest(business_problem="A" * 50)
        assert len(req.business_problem) == 50

    def test_valid_with_optional_fields(self):
        req = BlueprintRequest(
            business_problem="A" * 50,
            company_context="SAP environment",
            industry="Logistics",
        )
        assert req.company_context == "SAP environment"
        assert req.industry == "Logistics"

    def test_optional_fields_default_to_none(self):
        req = BlueprintRequest(business_problem="A" * 50)
        assert req.company_context is None
        assert req.industry is None

    def test_strips_whitespace(self):
        req = BlueprintRequest(business_problem="  " + "A" * 50 + "  ")
        assert not req.business_problem.startswith(" ")
        assert not req.business_problem.endswith(" ")

    def test_too_short_raises(self):
        with pytest.raises(ValidationError, match="at least 50 characters"):
            BlueprintRequest(business_problem="too short")

    def test_too_long_raises(self):
        with pytest.raises(ValidationError, match="5000 characters"):
            BlueprintRequest(business_problem="A" * 5001)

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            BlueprintRequest()  # type: ignore[call-arg]


class TestSolutionType:
    def test_all_values_accepted(self):
        for value in ("RAG", "AGENTIC", "AUTOMATION", "FORECASTING", "OCR", "API_INTEGRATION", "HYBRID"):
            assert SolutionType(value) is not None

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            SolutionType("UNKNOWN")


class TestPromptTemplate:
    def test_prompt_template_file_exists(self):
        path = Path(__file__).parent.parent / "app" / "core" / "prompt_templates.py"
        assert path.exists(), "app/core/prompt_templates.py is missing"

    def test_system_prompt_is_non_empty(self):
        assert len(SYSTEM_PROMPT) > 200, "SYSTEM_PROMPT is suspiciously short"

    def test_system_prompt_instructs_json_only(self):
        assert "JSON" in SYSTEM_PROMPT, "SYSTEM_PROMPT must instruct the LLM to return JSON only"

    def test_system_prompt_contains_all_required_output_fields(self):
        missing = [f for f in _REQUIRED_OUTPUT_FIELDS if f not in SYSTEM_PROMPT]
        assert not missing, (
            f"SYSTEM_PROMPT is missing output field references: {missing}. "
            "Update app/core/prompt_templates.py to include all 14 required fields."
        )
