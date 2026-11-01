"""仪表盘聚合接口测试"""
import pytest

from tests.factories import AssetFactory, VulnerabilityAssetFactory, VulnerabilityFactory


@pytest.mark.django_db
def test_dashboard_requires_auth(api_client):
    assert api_client.get("/api/v1/dashboard/").status_code == 401


@pytest.mark.django_db
def test_dashboard_metrics_and_trend(api_client, auth_headers):
    asset = AssetFactory(importance=3)
    v = VulnerabilityFactory(status="unverified", risk_level="high", cvss_score=8.0)
    VulnerabilityAssetFactory(asset=asset, vulnerability=v)

    resp = api_client.get("/api/v1/dashboard/", **auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]

    metrics = data["metrics"]
    assert metrics["asset_total"] >= 1
    assert metrics["vuln_total"] >= 1
    assert "open_vuln_count" in metrics and "overdue_tickets" in metrics

    assert len(data["trend"]) == 14
    assert "top_risk_assets" in data
    assert "vuln_by_risk" in data
    assert "recent_vulns" in data and "recent_tickets" in data
