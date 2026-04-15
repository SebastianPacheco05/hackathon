"""Tests HTTP de rutas de inteligencia de negocio (sin LLM)."""
import pytest
from fastapi.testclient import TestClient

from main import app


def test_business_endpoints_require_auth():
    """Sin JWT admin, los endpoints deben rechazar."""
    client = TestClient(app)
    paths = [
        "/api/admin/ai/predictions/demand",
        "/api/admin/ai/recommendations/production",
        "/api/admin/ai/alerts/anomalies",
        "/api/admin/ai/export/readiness",
        "/api/admin/ai/insights",
    ]
    for path in paths:
        r = client.get(path)
        assert r.status_code in (401, 403), f"{path} -> {r.status_code}"


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


def test_build_insights_payload_shape(db_session):
    from services.admin_ai_business_intel import build_business_insights

    out = build_business_insights(db_session)
    assert "summary" in out
    assert "data" in out
    assert "recommendations" in out
    assert "generated_at" in out
    assert isinstance(out["data"], dict)
