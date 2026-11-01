"""风险评分纯函数测试"""
import pytest

from app.services.risk_score import (
    asset_risk_score,
    risk_level_from_score,
    score_vulnerability,
)
from tests.factories import AssetFactory, VulnerabilityAssetFactory, VulnerabilityFactory


@pytest.mark.django_db
def test_score_uses_cvss_and_importance_weight():
    asset = AssetFactory(importance=4)  # 核心权重 1.6
    v = VulnerabilityFactory(cvss_score=10.0, risk_level="critical")
    # 10 * 1.6 = 16.0
    assert score_vulnerability(v, asset) == pytest.approx(16.0)


@pytest.mark.django_db
def test_score_falls_back_to_weight_when_no_cvss():
    asset = AssetFactory(importance=1)  # 权重 0.8
    v = VulnerabilityFactory(cvss_score=None, risk_level="high")  # high 权重 3 -> 7.5
    assert score_vulnerability(v, asset) == pytest.approx(6.0)


@pytest.mark.django_db
def test_score_capped_at_100():
    asset = AssetFactory(importance=4)
    v = VulnerabilityFactory(cvss_score=100.0)
    assert score_vulnerability(v, asset) == 100.0


@pytest.mark.parametrize(
    "score,expected",
    [
        (0, "info"),
        (10, "low"),
        (30, "medium"),
        (60, "high"),
        (90, "critical"),
    ],
)
def test_risk_level_from_score(score, expected):
    assert risk_level_from_score(score) == expected


@pytest.mark.django_db
def test_asset_risk_score_aggregates_open_and_ignores_closed():
    asset = AssetFactory(importance=3)  # 权重 1.3
    open_v = VulnerabilityFactory(cvss_score=10.0, status="unverified")
    closed_v = VulnerabilityFactory(cvss_score=10.0, status="closed")  # 不计入
    VulnerabilityAssetFactory(asset=asset, vulnerability=open_v)
    VulnerabilityAssetFactory(asset=asset, vulnerability=closed_v)
    # 仅 open_v 计入: 10 * 1.3 = 13.0
    assert asset_risk_score(asset) == pytest.approx(13.0)


@pytest.mark.django_db
def test_asset_risk_score_zero_when_no_open_vulns():
    asset = AssetFactory(importance=3)
    closed_v = VulnerabilityFactory(cvss_score=10.0, status="closed")
    VulnerabilityAssetFactory(asset=asset, vulnerability=closed_v)
    assert asset_risk_score(asset) == 0.0
