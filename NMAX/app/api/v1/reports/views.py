"""合规报表导出：等保合规视图（概览 + 资产明细 + 漏洞清单）/ 漏洞清单 Excel"""
import io

from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from rest_framework.views import APIView

from app.libs.permission.data_scope import filter_by_data_scope, get_data_scope
from app.libs.permission.permission import HasPermission
from app.models.assets.assets import Asset
from app.models.vulnerabilities.vulnerability import Vulnerability
from app.services.risk_score import asset_risk_score

OPEN_VULN_STATUS = ("unverified", "verified", "fixing", "pending_retest")
RISK_LABEL = {"critical": "严重", "high": "高危", "medium": "中危", "low": "低危", "info": "信息"}
IMPORTANCE_LABEL = {1: "低", 2: "中", 3: "高", 4: "核心"}

HEADER_FILL = PatternFill("solid", fgColor="1A2540")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
TITLE_FONT = Font(color="FFFFFF", bold=True, size=14)


def _vuln_scope_qs(user):
    qs = Vulnerability.objects.filter(is_deleted=False)
    is_all, dept_ids = get_data_scope(user)
    if not is_all:
        if dept_ids:
            qs = qs.filter(assets__asset__department_id__in=list(dept_ids))
        else:
            qs = qs.filter(created_by=user)
    return qs.distinct()


def _style_header(ws, row=1, ncols=None):
    ncols = ncols or ws.max_column
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 26


def _set_widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _build_compliance_workbook(user):
    assets_qs = filter_by_data_scope(
        Asset.objects.filter(is_deleted=False), user, dept_field="department"
    ).prefetch_related("vulnerabilities__vulnerability")
    vulns_qs = _vuln_scope_qs(user)

    wb = Workbook()

    # 概览
    ws0 = wb.active
    ws0.title = "合规概览"
    ws0.merge_cells("A1:D1")
    ws0["A1"] = "NMA 安全合规概览报表"
    ws0["A1"].font = TITLE_FONT
    ws0["A1"].fill = HEADER_FILL
    ws0["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws0.row_dimensions[1].height = 30

    asset_total = assets_qs.count()
    vuln_total = vulns_qs.count()
    open_vulns = vulns_qs.filter(status__in=OPEN_VULN_STATUS).count()
    critical_high = vulns_qs.filter(risk_level__in=("critical", "high")).count()
    now = timezone.now()
    overview = [
        ("生成时间", now.strftime("%Y-%m-%d %H:%M:%S")),
        ("资产总数", asset_total),
        ("漏洞总数", vuln_total),
        ("未修复漏洞数", open_vulns),
        ("严重+高危漏洞数", critical_high),
        ("资产暴露面(已标记暴露)", assets_qs.filter(exposed=True).count()),
    ]
    ws0.append([])
    ws0.append(["指标", "数值"])
    _style_header(ws0, row=3, ncols=2)
    for label, value in overview:
        ws0.append([label, value])
    _set_widths(ws0, [28, 40])

    # 资产合规明细
    ws1 = wb.create_sheet("资产合规明细")
    headers = ["资产名称", "IP", "安全等级", "重要程度", "开放漏洞数", "严重", "高危", "资产风险分", "合规状态"]
    ws1.append(headers)
    _style_header(ws1, ncols=len(headers))
    for asset in assets_qs.order_by("name"):
        crit = high = 0
        open_count = 0
        for va in asset.vulnerabilities.all():
            v = va.vulnerability
            if v.is_deleted or v.status not in OPEN_VULN_STATUS:
                continue
            open_count += 1
            if v.risk_level == "critical":
                crit += 1
            elif v.risk_level == "high":
                high += 1
        score = asset_risk_score(asset)
        status = "不达标" if (crit or high) else "达标"
        ws1.append([
            asset.name, asset.ip, asset.security_level or "-",
            IMPORTANCE_LABEL.get(asset.importance, str(asset.importance)),
            open_count, crit, high, score, status,
        ])
    _set_widths(ws1, [22, 16, 10, 10, 12, 8, 8, 12, 12])

    # 漏洞清单
    ws2 = wb.create_sheet("漏洞清单")
    headers = ["漏洞名称", "CVE编号", "风险等级", "状态", "来源", "关联资产", "资产IP", "SLA截止", "发现时间"]
    ws2.append(headers)
    _style_header(ws2, ncols=len(headers))
    for v in vulns_qs.order_by("-discovered_at"):
        link = v.assets.first()
        ws2.append([
            v.name, v.cve_id or "-", RISK_LABEL.get(v.risk_level, v.risk_level),
            v.status, v.source, link.asset.name if link else "-",
            link.asset.ip if link else "-",
            v.sla_due_at.strftime("%Y-%m-%d %H:%M") if v.sla_due_at else "-",
            v.discovered_at.strftime("%Y-%m-%d %H:%M") if v.discovered_at else "-",
        ])
    _set_widths(ws2, [30, 18, 10, 12, 12, 18, 16, 18, 18])

    return wb


def _build_vuln_workbook(user):
    wb = Workbook()
    ws = wb.active
    ws.title = "漏洞清单"
    headers = ["ID", "名称", "CVE编号", "风险等级", "CVSS", "状态", "来源", "类型", "关联资产", "端口", "发现时间"]
    ws.append(headers)
    _style_header(ws, ncols=len(headers))
    for v in _vuln_scope_qs(user).order_by("-discovered_at"):
        link = v.assets.first()
        ws.append([
            v.id, v.name, v.cve_id or "-", RISK_LABEL.get(v.risk_level, v.risk_level),
            v.cvss_score or "-", v.status, v.source, v.vuln_type,
            link.asset.name if link else "-", link.port if link else "-",
            v.discovered_at.strftime("%Y-%m-%d %H:%M") if v.discovered_at else "-",
        ])
    _set_widths(ws, [8, 30, 18, 10, 8, 12, 12, 16, 18, 10, 18])
    return wb


def _xlsx_response(wb, filename):
    buf = io.BytesIO()
    wb.save(buf)
    return HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


class ReportsView(APIView):
    permission_classes = (HasPermission,)
    required_permissions = ["report:view"]

    def get(self, request):
        report_type = request.query_params.get("type", "compliance")
        if report_type == "vulnerabilities":
            wb = _build_vuln_workbook(request.user)
            filename = "vulnerabilities.xlsx"
        else:
            wb = _build_compliance_workbook(request.user)
            filename = "compliance_report.xlsx"
        return _xlsx_response(wb, filename)
