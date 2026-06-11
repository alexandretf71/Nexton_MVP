from tests.fixtures.sample_problems import (
    FINANCE_FORECASTING,
    HR_KNOWLEDGE_BASE,
    LOGISTICS_INVOICE,
)


class TestHealthEndpoint:
    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_status_is_ok(self, client):
        assert client.get("/health").json()["status"] == "ok"

    def test_reports_mock_provider(self, client):
        assert client.get("/health").json()["provider"] == "mock"

    def test_returns_version(self, client):
        data = client.get("/health").json()
        assert "version" in data
        assert data["version"]


class TestGenerateBlueprintEndpoint:
    def test_valid_request_returns_200(self, client):
        response = client.post("/generate-blueprint", json=LOGISTICS_INVOICE)
        assert response.status_code == 200

    def test_success_flag_is_true(self, client):
        response = client.post("/generate-blueprint", json=LOGISTICS_INVOICE)
        assert response.json()["success"] is True

    def test_all_ten_sections_present(self, client):
        data = client.post("/generate-blueprint", json=LOGISTICS_INVOICE).json()["data"]
        assert data["business_problem_summary"]
        assert data["ai_opportunity_classification"]
        assert data["recommended_solution_type"]
        assert data["suggested_architecture"]
        assert data["agentic_workflow"]
        assert data["engineering_backlog"]
        assert data["risks_and_assumptions"]
        assert data["testing_plan"]
        assert data["executive_summary"]
        assert data["delivery_status_report"]

    def test_metadata_fields_present(self, client):
        data = client.post("/generate-blueprint", json=LOGISTICS_INVOICE).json()["data"]
        assert data["generated_at"]
        assert data["provider_used"] == "mock"

    def test_with_optional_fields(self, client):
        response = client.post("/generate-blueprint", json=HR_KNOWLEDGE_BASE)
        assert response.status_code == 200

    def test_without_optional_fields(self, client):
        response = client.post(
            "/generate-blueprint",
            json={"business_problem": "A" * 50},
        )
        assert response.status_code == 200

    def test_problem_too_short_returns_422(self, client):
        response = client.post(
            "/generate-blueprint",
            json={"business_problem": "too short"},
        )
        assert response.status_code == 422

    def test_missing_required_field_returns_422(self, client):
        response = client.post("/generate-blueprint", json={})
        assert response.status_code == 422

    def test_all_three_sample_problems(self, client):
        for problem in (LOGISTICS_INVOICE, HR_KNOWLEDGE_BASE, FINANCE_FORECASTING):
            response = client.post("/generate-blueprint", json=problem)
            assert response.status_code == 200
            assert response.json()["success"] is True

    def test_anthropic_provider_without_key_returns_400(self, client):
        response = client.post(
            "/generate-blueprint",
            json={"business_problem": "A" * 50},
            headers={"X-LLM-Provider": "anthropic"},
        )
        assert response.status_code == 400
        assert "X-API-Key" in response.json()["detail"]

    def test_openai_provider_without_key_returns_400(self, client):
        response = client.post(
            "/generate-blueprint",
            json={"business_problem": "A" * 50},
            headers={"X-LLM-Provider": "openai"},
        )
        assert response.status_code == 400
        assert "X-API-Key" in response.json()["detail"]
