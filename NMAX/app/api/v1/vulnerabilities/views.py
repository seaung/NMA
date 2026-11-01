from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from app.libs.permission.data_scope import get_data_scope
from app.libs.permission.permission import HasPermission
from app.models.assets.assets import Asset
from app.models.vulnerabilities.vulnerability import Vulnerability
from app.services.excel_utils import build_excel_response, read_excel_rows
from app.services.state_machine import transition_vulnerability
from app.services.vuln_service import build_fingerprint

from .serializers import VulnerabilitySerializer

EXPORT_HEADERS = [
    "ID", "名称", "CVE编号", "风险等级", "CVSS", "状态", "来源", "漏洞类型",
    "资产IP", "端口", "描述", "影响范围", "修复建议", "发现时间", "风险评分",
]


class VulnerabilityViewSet(viewsets.ModelViewSet):
    """漏洞管理：增删改查 + 数据范围 + 状态机流转 + 导入导出"""

    permission_classes = (HasPermission,)
    required_permissions = ["vuln:view"]
    serializer_class = VulnerabilitySerializer
    queryset = Vulnerability.objects.all()

    def get_queryset(self):
        qs = super().get_queryset().filter(is_deleted=False)
        is_all, dept_ids = get_data_scope(self.request.user)
        if not is_all:
            if dept_ids:
                qs = qs.filter(assets__asset__department_id__in=list(dept_ids))
            else:
                qs = qs.filter(created_by=self.request.user)
        qs = qs.distinct()

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(cve_id__icontains=search)
                | Q(description__icontains=search)
            )
        risk_level = self.request.query_params.get("risk_level")
        if risk_level:
            qs = qs.filter(risk_level=risk_level)
        state = self.request.query_params.get("status")
        if state:
            qs = qs.filter(status=state)
        source = self.request.query_params.get("source")
        if source:
            qs = qs.filter(source=source)
        asset_id = self.request.query_params.get("asset_id")
        if asset_id:
            qs = qs.filter(assets__asset_id=asset_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request: Request, *args, **kwargs):
        vuln = self.get_object()
        vuln.is_deleted = True
        vuln.deleted_at = timezone.now()
        vuln.save(update_fields=["is_deleted", "deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def transition(self, request: Request, pk=None):
        vuln = self.get_object()
        to_status = request.data.get("status") or request.data.get("to_status")
        note = request.data.get("note", "")
        if not to_status:
            raise ValidationError({"status": "缺少目标状态"})
        try:
            transition_vulnerability(vuln, to_status, request.user, note)
        except ValueError as e:
            raise ValidationError({"status": str(e)})
        return Response(self.get_serializer(vuln).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def export_excel(self, request: Request):
        rows = []
        for v in self.get_queryset().order_by("-discovered_at"):
            link = v.assets.first()
            from app.services.risk_score import score_vulnerability

            rows.append([
                v.id, v.name, v.cve_id or "", v.risk_level, v.cvss_score or "",
                v.status, v.source, v.vuln_type,
                link.asset.ip if link else "", link.port if link else "",
                v.description, v.impact, v.solution,
                v.discovered_at.strftime("%Y-%m-%d %H:%M") if v.discovered_at else "",
                score_vulnerability(v, link.asset if link else None),
            ])
        return build_excel_response(EXPORT_HEADERS, rows, "vulnerabilities.xlsx")

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser])
    def import_excel(self, request: Request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            raise ValidationError({"file": "缺少上传文件"})
        rows = read_excel_rows(file_obj)
        created, skipped, errors = 0, 0, []
        for idx, row in enumerate(rows, start=2):
            name = (row.get("名称") or row.get("name") or "").strip()
            if not name:
                skipped += 1
                continue
            cve_id = (row.get("CVE编号") or row.get("cve_id") or "").strip() or None
            fingerprint = build_fingerprint(name, cve_id, row.get("漏洞类型", "") or "")
            if Vulnerability.objects.filter(fingerprint=fingerprint, is_deleted=False).exists():
                skipped += 1
                continue
            try:
                vuln = Vulnerability.objects.create(
                    name=name,
                    cve_id=cve_id,
                    risk_level=(row.get("风险等级") or row.get("risk_level") or "medium"),
                    cvss_score=_to_float(row.get("CVSS") or row.get("cvss_score")),
                    status=(row.get("状态") or row.get("status") or "unverified"),
                    source=(row.get("来源") or row.get("source") or "import"),
                    vuln_type=(row.get("漏洞类型") or row.get("vuln_type") or "").strip(),
                    description=(row.get("描述") or row.get("description") or "").strip(),
                    impact=(row.get("影响范围") or row.get("impact") or "").strip(),
                    solution=(row.get("修复建议") or row.get("solution") or "").strip(),
                    fingerprint=fingerprint,
                    created_by=request.user,
                )
                asset_ip = (row.get("资产IP") or row.get("asset_ip") or "").strip()
                if asset_ip:
                    asset = Asset.objects.filter(ip=asset_ip, is_deleted=False).first()
                    if asset:
                        from app.models.vulnerabilities.vulnerability import VulnerabilityAsset

                        VulnerabilityAsset.objects.create(
                            vulnerability=vuln, asset=asset,
                            port=(row.get("端口") or "").strip(),
                            protocol=(row.get("协议") or "").strip(),
                        )
                created += 1
            except Exception as e:  # noqa: BLE001
                errors.append(f"第{idx}行: {e}")
        return Response({"created": created, "skipped": skipped, "errors": errors})


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
