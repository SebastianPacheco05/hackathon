"""Tests inteligencia de negocio admin AI (tools + payloads)."""
import pytest

from services.admin_ai_tools import ADMIN_AI_TOOLS
from services.admin_ai_business_intel import format_business_payload_markdown


BUSINESS_TOOLS = (
    "predict_demand",
    "recommend_production",
    "detect_anomalies",
    "analyze_export_readiness",
    "get_business_insights",
)


def test_business_tools_registered():
    names = [t["function"]["name"] for t in ADMIN_AI_TOOLS if "function" in t]
    for name in BUSINESS_TOOLS:
        assert name in names, f"Falta tool {name}"


def test_format_business_payload_markdown():
    md = format_business_payload_markdown(
        {
            "summary": "Test summary",
            "data": {"k": 1},
            "recommendations": ["Do A", "Do B"],
            "generated_at": "2025-01-01T00:00:00Z",
        }
    )
    assert "Test summary" in md
    assert "Do A" in md
    assert "json" in md.lower() or "k" in md


@pytest.fixture
def db_session():
    from core.config import settings

    if not getattr(settings, "DATABASE_URL", None):
        pytest.skip("DATABASE_URL no configurada")
    from core.database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.mark.parametrize("action", BUSINESS_TOOLS)
def test_execute_business_actions_return_str(db_session, action):
    from services.admin_ai_actions import execute_action

    params = {}
    if action == "predict_demand":
        params = {"time_range": 30}
    elif action == "recommend_production":
        params = {"time_range": 30, "safety_factor": 1.1}
    elif action == "detect_anomalies":
        params = {"days_recent": 14, "days_baseline": 28}
    elif action == "analyze_export_readiness":
        params = {"limit": 5}

    result = execute_action(db_session, action, params, 1)
    assert isinstance(result, str)
    assert len(result) > 0
