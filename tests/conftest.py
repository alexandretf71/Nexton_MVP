import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import BlueprintRequest
from app.services.llm.mock import MockLLMProvider
from tests.fixtures.sample_problems import LOGISTICS_INVOICE


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_provider():
    return MockLLMProvider()


@pytest.fixture
def sample_request() -> BlueprintRequest:
    return BlueprintRequest(**LOGISTICS_INVOICE)
