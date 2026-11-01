"""漏洞状态机：强校验状态流转并记录历史"""
from __future__ import annotations

from django.utils import timezone

from app.models.vulnerabilities.vulnerability import (
    Vulnerability,
    VulnerabilityHistory,
)
from app.models.workflow.ticket import VulnerabilityTicket

# 允许的漏洞状态流转（key=当前状态, value=可流转到的目标状态）
VULN_TRANSITIONS = {
    "unverified": ["verified", "false_positive", "risk_accepted", "closed"],
    "verified": ["fixing", "false_positive", "risk_accepted", "closed"],
    "fixing": ["pending_retest", "risk_accepted", "closed"],
    "pending_retest": ["fixed", "fixing", "risk_accepted", "closed"],
    "fixed": ["closed", "pending_retest", "risk_accepted"],
    "closed": ["unverified"],          # 重新打开
    "false_positive": ["unverified"],  # 误报纠正
    "risk_accepted": ["unverified", "closed"],
}

STATUS_LABELS = {
    "unverified": "未验证",
    "verified": "已验证",
    "fixing": "修复中",
    "pending_retest": "待复测",
    "fixed": "已修复",
    "closed": "已关闭",
    "false_positive": "误报",
    "risk_accepted": "风险接受",
}


def can_transition(current: str, target: str) -> bool:
    return target in VULN_TRANSITIONS.get(current, [])


def transition_vulnerability(
    vuln: Vulnerability, to_status: str, user, note: str = ""
) -> Vulnerability:
    """执行漏洞状态流转，校验不通过抛出异常，成功写入历史。"""
    current = vuln.status
    if current == to_status:
        return vuln
    if not can_transition(current, to_status):
        raise ValueError(
            f"不允许的状态流转：{STATUS_LABELS.get(current, current)} → "
            f"{STATUS_LABELS.get(to_status, to_status)}"
        )

    old_status = current
    vuln.status = to_status
    now = timezone.now()
    if to_status == "verified" and not vuln.verified_at:
        vuln.verified_at = now
    if to_status == "fixed" and not vuln.fixed_at:
        vuln.fixed_at = now
    if to_status == "closed" and not vuln.closed_at:
        vuln.closed_at = now
    if to_status in ("unverified", "false_positive"):
        # 重新打开 / 取消误报：清空终态时间
        if to_status == "unverified":
            vuln.verified_at = None
            vuln.fixed_at = None
            vuln.closed_at = None
    vuln.save(
        update_fields=["status", "verified_at", "fixed_at", "closed_at", "updated_at"]
    )

    VulnerabilityHistory.objects.create(
        vulnerability=vuln,
        operator=user,
        old_status=old_status,
        new_status=to_status,
        note=note,
    )
    return vuln


# ---------------------------------------------------------------------------
# 工单状态机
# ---------------------------------------------------------------------------
TICKET_TRANSITIONS = {
    "created": ["assigned", "rejected", "closed"],
    "assigned": ["processing", "rejected", "closed"],
    "processing": ["pending_verify", "rejected", "closed"],
    "pending_verify": ["resolved", "processing", "closed"],
    "resolved": ["closed", "reopened"],
    "closed": ["reopened"],
    "rejected": ["created", "closed"],
    "reopened": ["processing", "closed"],
}

TICKET_STATUS_LABELS = {
    "created": "已创建",
    "assigned": "已分配",
    "processing": "处理中",
    "pending_verify": "待验证",
    "resolved": "已解决",
    "closed": "已关闭",
    "rejected": "已拒绝",
    "reopened": "重新打开",
}

# SLA 默认时长（小时），可被 SystemConfig 覆盖
DEFAULT_SLA_HOURS = {
    "critical": 24,
    "high": 72,
    "medium": 168,
    "low": 720,
}


def can_transition_ticket(current: str, target: str) -> bool:
    return target in TICKET_TRANSITIONS.get(current, [])


def get_sla_hours(priority: str) -> int:
    from app.models.system.system_config import SystemConfig

    key = f"sla_{priority}_hours"
    val = SystemConfig.get_value(key)
    if isinstance(val, (int, float)):
        return int(val)
    return DEFAULT_SLA_HOURS.get(priority, 168)


def compute_ticket_deadline(priority: str):
    return timezone.now() + timezone.timedelta(hours=get_sla_hours(priority))


def is_ticket_overdue(ticket) -> bool:
    if ticket.status in ("resolved", "closed"):
        return False
    if not ticket.deadline:
        return False
    return ticket.deadline < timezone.now()


def transition_ticket(
    ticket, to_status: str, user, note: str = "", resolution: str | None = None
) -> VulnerabilityTicket:
    """执行工单状态流转，校验不通过抛出异常，成功写入历史。"""

    current = ticket.status
    if current == to_status:
        return ticket
    if not can_transition_ticket(current, to_status):
        raise ValueError(
            f"不允许的工单流转：{TICKET_STATUS_LABELS.get(current, current)} → "
            f"{TICKET_STATUS_LABELS.get(to_status, to_status)}"
        )

    old_status = current
    ticket.status = to_status
    now = timezone.now()
    if to_status == "resolved":
        if resolution is not None:
            ticket.resolution = resolution
    if to_status in ("resolved", "closed") and not ticket.closed_at:
        ticket.closed_at = now
    if to_status in ("created", "reopened", "rejected"):
        # 重新打开/退回：清空关闭时间
        if to_status != "closed":
            ticket.closed_at = None
    ticket.save(
        update_fields=["status", "resolution", "closed_at", "updated_at"]
    )

    from app.models.workflow.ticket import TicketHistory

    TicketHistory.objects.create(
        ticket=ticket,
        operator=user,
        action="transition",
        old_status=old_status,
        new_status=to_status,
        comment=note,
    )
    return ticket
