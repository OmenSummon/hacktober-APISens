import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.findings import Finding, FindingDetail, FindingType, SeverityLevel


@pytest.mark.anyio
async def test_ai_analyze_fallback_offline():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        finding = Finding(
            id="f-test-1",
            type=FindingType.SHADOW_ENDPOINT,
            severity=SeverityLevel.HIGH,
            method="GET",
            endpoint="GET /admin/users",
            path="/admin/users",
            title="Undocumented endpoint",
            description="Detected shadow route",
            risk_score=85,
            details=FindingDetail(),
        )

        response = await client.post(
            "/api/ai/analyze",
            json={"finding": finding.model_dump()},
        )
        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "security_impact" in data
        assert "recommended_remediation" in data
        assert "suggested_openapi_patch" in data
        assert data["provider"] in ("deterministic_engine", "ollama")
        assert len(data["explanation"]) > 20
