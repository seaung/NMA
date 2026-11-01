"""漏洞风险评分：CVSS 基准叠加资产重要度权重，归一化到 0-100；并提供资产聚合评分"""
from app.models.vulnerabilities.vulnerability import Vulnerability

RISK_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
IMPORTANCE_WEIGHT = {1: 0.8, 2: 1.0, 3: 1.3, 4: 1.6}
# 不计入有效风险敞口的状态
IGNORED_STATUSES = {"closed", "false_positive", "risk_accepted"}


def score_vulnerability(vuln: Vulnerability, asset=None) -> float:
    """单漏洞风险评分：CVSS × 资产重要度权重，上限 100。"""
    base = vuln.cvss_score
    if base is None:
        base = RISK_WEIGHT.get(vuln.risk_level, 0) * 2.5
    imp = IMPORTANCE_WEIGHT.get(getattr(asset, "importance", None), 1.0)
    return round(min(base * imp, 100.0), 1)


def risk_level_from_score(score: float) -> str:
    if score >= 80:
        return "critical"
    if score >= 50:
        return "high"
    if score >= 25:
        return "medium"
    if score > 0:
        return "low"
    return "info"


def asset_risk_score(asset) -> float:
    """资产聚合风险评分：对其有效（未关闭/未误报/未接受）漏洞评分求和并封顶 100。"""
    scores = []
    for va in asset.vulnerabilities.select_related("vulnerability").all():
        v = va.vulnerability
        if v.is_deleted or v.status in IGNORED_STATUSES:
            continue
        scores.append(score_vulnerability(v, asset))
    if not scores:
        return 0.0
    return round(min(100.0, float(sum(scores))), 1)
