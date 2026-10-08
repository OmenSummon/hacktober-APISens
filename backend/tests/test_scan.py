import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.demo_data import DEMO_OPENAPI_SPEC, DEMO_TRAFFIC_REQUESTS


@pytest.mark.anyio
async def test_demo_scan_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/demo")
        assert response.status_code == 200
        data = response.json()

        summary = data["summary"]
        assert summary["total_documented_endpoints"] == 5
        assert summary["shadow_endpoints"] >= 2  # /admin/users and /debug
        assert summary["schema_drifts"] >= 1     # coupon
        assert summary["risk_score"] > 50
        assert summary["risk_level"] in ("HIGH", "CRITICAL")

        # Verify inventory list
        inventory = data["inventory"]
        assert len(inventory) >= 6
        assert any(item["endpoint"] == "/admin/users" and item["status"] == "SHADOW" for item in inventory)
        assert any(item["endpoint"] == "/users/{id}" and item["status"] == "HEALTHY" for item in inventory)

        # Verify findings list
        findings = data["findings"]
        assert len(findings) >= 3


@pytest.mark.anyio
async def test_custom_scan_endpoint():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {
            "openapi_spec": DEMO_OPENAPI_SPEC,
            "traffic": DEMO_TRAFFIC_REQUESTS,
        }
        response = await client.post("/api/scan", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["summary"]["shadow_endpoints"] >= 2

        # Verify findings endpoint retrieves them
        findings_resp = await client.get("/api/findings")
        assert findings_resp.status_code == 200
        findings = findings_resp.json()
        assert len(findings) >= 3


@pytest.mark.anyio
async def test_scan_validation_error():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Invalid spec
        payload = {
            "openapi_spec": "invalid: yaml: [",
            "traffic": [],
        }
        response = await client.post("/api/scan", json=payload)
        assert response.status_code in (400, 422)
