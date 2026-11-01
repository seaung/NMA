"""状态机测试：漏洞流转 / 工单流转的强校验与历史记录"""
import pytest

from app.models.vulnerabilities.vulnerability import VulnerabilityHistory
from app.models.workflow.ticket import TicketHistory
from app.services.state_machine import (
    transition_ticket,
    transition_vulnerability,
)
from tests.factories import TicketFactory, UserFactory, VulnerabilityFactory


@pytest.mark.django_db
def test_vuln_valid_transition_updates_status_and_history():
    user = UserFactory()
    v = VulnerabilityFactory(status="unverified")
    transition_vulnerability(v, "verified", user, note="验证通过")
    v.refresh_from_db()
    assert v.status == "verified"
    assert v.verified_at is not None
    assert VulnerabilityHistory.objects.filter(
        vulnerability=v, old_status="unverified", new_status="verified"
    ).exists()


@pytest.mark.django_db
def test_vuln_invalid_transition_raises():
    user = UserFactory()
    v = VulnerabilityFactory(status="unverified")
    with pytest.raises(ValueError):
        # unverified -> fixing 不在允许列表
        transition_vulnerability(v, "fixing", user)


@pytest.mark.django_db
def test_same_status_is_noop():
    user = UserFactory()
    v = VulnerabilityFactory(status="unverified")
    before = VulnerabilityHistory.objects.count()
    transition_vulnerability(v, "unverified", user)
    assert VulnerabilityHistory.objects.count() == before


@pytest.mark.django_db
def test_ticket_valid_transition():
    user = UserFactory()
    t = TicketFactory(status="created")
    transition_ticket(t, "assigned", user, note="指派处理")
    t.refresh_from_db()
    assert t.status == "assigned"
    assert TicketHistory.objects.filter(ticket=t, new_status="assigned").exists()


@pytest.mark.django_db
def test_ticket_invalid_transition_raises():
    user = UserFactory()
    t = TicketFactory(status="created")
    with pytest.raises(ValueError):
        # created -> processing 不在允许列表
        transition_ticket(t, "processing", user)
