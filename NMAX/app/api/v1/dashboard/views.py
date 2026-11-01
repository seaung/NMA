"""仪表盘聚合统计：指标卡、风险分布、发现/修复趋势、Top 风险资产、最近动态"""
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from app.libs.permission.data_scope import filter_by_data_scope, get_data_scope
from app.libs.permission.permission import HasPermission
from app.models.assets.assets import Asset
from app.models.vulnerabilities.vulnerability import Vulnerability
from app.models.workflow.ticket import VulnerabilityTicket
from app.services.risk_score import asset_risk_score, risk_level_from_score

OPEN_VULN_STATUS = ("unverified", "verified", "fixing", "pending_retest")
RESOLVED_TICKET_STATUS = ("closed", "resolved", "rejected")
ACTIVE_TICKET_STATUS = ("created", "assigned", "processing", "pending_verify", "reopened")


def _vuln_scope_qs(user):
    qs = Vulnerability.objects.filter(is_deleted=False)
    is_all, dept_ids = get_data_scope(user)
    if not is_all:
        if dept_ids:
            qs = qs.filter(assets__asset__department_id__in=list(dept_ids))
        else:
            qs = qs.filter(created_by=user)
    return qs.distinct()


class DashboardView(APIView):
    permission_classes = (HasPermission,)
    # 仪表盘为登录即可见，不强制特定权限码

    def get(self, request):
        user = request.user
        now = timezone.now()

        assets_qs = filter_by_data_scope(Asset.objects.filter(is_deleted=False), user, dept_field="department")
        vulns_qs = _vuln_scope_qs(user)
        tickets_qs = filter_by_data_scope(
            VulnerabilityTicket.objects.all(), user, dept_field="department", owner_field="creator"
        )

        # 指标卡
        asset_total = assets_qs.count()
        vuln_total = vulns_qs.count()
        open_vuln_count = vulns_qs.filter(status__in=OPEN_VULN_STATUS).count()
        fixed_vuln_count = vulns_qs.filter(status__in=("fixed", "closed")).count()
        critical_high = vulns_qs.filter(risk_level__in=("critical", "high")).count()
        open_tickets = tickets_qs.filter(status__in=ACTIVE_TICKET_STATUS).count()
        overdue_tickets = tickets_qs.filter(
            deadline__lt=now, status__in=ACTIVE_TICKET_STATUS
        ).count()

        # 风险分布
        risk_by_level = (
            vulns_qs.values("risk_level").annotate(count=Count("id")).order_by("risk_level")
        )
        vuln_by_risk = [
            {"level": item["risk_level"], "count": item["count"]} for item in risk_by_level
        ]

        # 状态分布
        status_dist = (
            vulns_qs.values("status").annotate(count=Count("id")).order_by("status")
        )
        vuln_by_status = [
            {"status": item["status"], "count": item["count"]} for item in status_dist
        ]

        # 趋势（最近 14 天发现 / 修复）
        days = 14
        since = (now - timezone.timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        disc = (
            vulns_qs.filter(discovered_at__gte=since)
            .annotate(day=TruncDay("discovered_at"))
            .values("day").annotate(count=Count("id"))
        )
        disc_map = {d["day"].date().isoformat(): d["count"] for d in disc}
        fixed = (
            vulns_qs.filter(fixed_at__gte=since)
            .annotate(day=TruncDay("fixed_at"))
            .values("day").annotate(count=Count("id"))
        )
        fixed_map = {d["day"].date().isoformat(): d["count"] for d in fixed}
        trend = []
        for i in range(days):
            ds = (since + timezone.timedelta(days=i)).date().isoformat()
            trend.append({
                "date": ds[5:],
                "discovered": disc_map.get(ds, 0),
                "fixed": fixed_map.get(ds, 0),
            })

        # Top 风险资产
        top_assets = []
        for asset in assets_qs.prefetch_related("vulnerabilities__vulnerability"):
            score = asset_risk_score(asset)
            if score <= 0:
                continue
            open_count = asset.vulnerabilities.filter(
                vulnerability__is_deleted=False,
                vulnerability__status__in=OPEN_VULN_STATUS,
            ).count()
            top_assets.append({
                "id": asset.id,
                "name": asset.name,
                "ip": asset.ip,
                "security_level": asset.security_level,
                "importance": asset.importance,
                "risk_score": score,
                "risk_level": risk_level_from_score(score),
                "open_vulns": open_count,
            })
        top_assets.sort(key=lambda x: x["risk_score"], reverse=True)
        top_assets = top_assets[:6]

        # 最近动态
        recent_vulns = [
            {
                "id": v.id, "name": v.name, "risk_level": v.risk_level,
                "status": v.status, "discovered_at": v.discovered_at,
            }
            for v in vulns_qs.order_by("-discovered_at")[:5]
        ]
        recent_tickets = [
            {
                "id": t.id, "title": t.title, "priority": t.priority,
                "status": t.status, "created_at": t.created_at,
            }
            for t in tickets_qs.order_by("-created_at")[:5]
        ]

        return Response({
            "metrics": {
                "asset_total": asset_total,
                "vuln_total": vuln_total,
                "open_vuln_count": open_vuln_count,
                "fixed_vuln_count": fixed_vuln_count,
                "critical_high": critical_high,
                "open_tickets": open_tickets,
                "overdue_tickets": overdue_tickets,
            },
            "vuln_by_risk": vuln_by_risk,
            "vuln_by_status": vuln_by_status,
            "trend": trend,
            "top_risk_assets": top_assets,
            "recent_vulns": recent_vulns,
            "recent_tickets": recent_tickets,
        })
