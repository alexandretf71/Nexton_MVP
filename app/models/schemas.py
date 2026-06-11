from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class SolutionType(str, Enum):
    RAG = "RAG"
    AGENTIC = "AGENTIC"
    AUTOMATION = "AUTOMATION"
    FORECASTING = "FORECASTING"
    OCR = "OCR"
    API_INTEGRATION = "API_INTEGRATION"
    HYBRID = "HYBRID"


# ── Request ──────────────────────────────────────────────────────────────────

class BlueprintRequest(BaseModel):
    business_problem: str
    company_context: Optional[str] = None
    industry: Optional[str] = None

    @field_validator("business_problem")
    @classmethod
    def validate_business_problem(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 50:
            raise ValueError("business_problem must be at least 50 characters")
        if len(v) > 5000:
            raise ValueError("business_problem must not exceed 5000 characters")
        return v


# ── Output sub-models ─────────────────────────────────────────────────────────

class AIOpportunity(BaseModel):
    title: str
    description: str
    impact: str       # HIGH / MEDIUM / LOW
    feasibility: str  # HIGH / MEDIUM / LOW


class AgenticStep(BaseModel):
    step_number: int
    agent_name: str
    action: str
    input: str
    output: str
    tools_used: list[str]


class BacklogItem(BaseModel):
    id: str
    title: str
    description: str
    priority: str  # P0 / P1 / P2 / P3
    effort: str    # XS / S / M / L / XL
    phase: str     # Foundation / Core / Polish / Future


class RiskItem(BaseModel):
    id: str
    category: str     # Technical / Data / Organizational / Timeline
    description: str
    likelihood: str   # HIGH / MEDIUM / LOW
    impact: str       # HIGH / MEDIUM / LOW
    mitigation: str


class TestCase(BaseModel):
    id: str
    type: str          # Unit / Integration / E2E / Manual
    description: str
    expected_outcome: str


class DataRequirement(BaseModel):
    source: str
    description: str
    availability: str  # HIGH / MEDIUM / LOW
    notes: str


class IntegrationPoint(BaseModel):
    system: str
    integration_type: str  # API / File / Database / Webhook / Manual
    description: str
    complexity: str  # HIGH / MEDIUM / LOW


class Milestone(BaseModel):
    week: int
    title: str
    deliverables: list[str]
    owner: str


class TeamRole(BaseModel):
    role: str
    count: int
    seniority: str    # Junior / Mid / Senior / Lead
    allocation: str   # e.g. "Full-time", "50%"
    responsibilities: str
    reports_to: str   # manager's role name; top role reports to "AI Division Director"


class FulfillmentAction(BaseModel):
    week: int         # aligned with delivery_status_report weeks
    role: str
    action: str       # HIRE / INTERNAL_ALLOCATION / CONTRACTOR
    notes: str


class DeliveryTeam(BaseModel):
    roles: list[TeamRole]
    fulfillment_plan: list[FulfillmentAction]


# ── Primary output ────────────────────────────────────────────────────────────

class BlueprintOutput(BaseModel):
    business_problem_summary: str
    operational_pain_points: list[str]
    ai_opportunity_classification: list[AIOpportunity]
    recommended_solution_type: SolutionType
    suggested_architecture: str
    agentic_workflow: list[AgenticStep]
    data_requirements: list[DataRequirement]
    integration_points: list[IntegrationPoint]
    engineering_backlog: list[BacklogItem]
    risks_and_assumptions: list[RiskItem]
    testing_plan: list[TestCase]
    executive_summary: str
    delivery_status_report: list[Milestone]
    delivery_team: DeliveryTeam
    # Metadata injected by the generator, not the LLM
    generated_at: datetime
    provider_used: str
    model_id: Optional[str] = None


# ── API envelope ──────────────────────────────────────────────────────────────

class BlueprintResponse(BaseModel):
    success: bool
    data: Optional[BlueprintOutput] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    provider: str
    version: str
