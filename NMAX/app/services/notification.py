"""站内消息通知服务：工单流转、逾期等场景触发消息"""
from app.models.system.message import Message, MessageRecipient


def notify(
    recipients,  # iterable of User 或 user id
    title: str,
    content: str,
    message_type: str = "system",
    level: str = "info",
    link: str = "",
    sender=None,
) -> Message | None:
    """向一组接收者发送站内消息，自动建立接收状态记录。"""
    recipients = list(recipients or [])
    if not recipients:
        return None

    msg = Message.objects.create(
        title=title,
        content=content,
        message_type=message_type,
        level=level,
        link=link,
        sender=sender,
    )
    for r in recipients:
        uid = r.id if hasattr(r, "id") else r
        MessageRecipient.objects.get_or_create(message=msg, recipient_id=uid)
    return msg


def notify_ticket_assigned(ticket, assignee, operator):
    return notify(
        [assignee],
        f"工单已分配：{ticket.title}",
        f"优先级：{ticket.get_priority_display()}，请及时处理。",
        message_type="ticket",
        level="warning",
        link="/tickets",
        sender=operator,
    )


def notify_ticket_status(ticket, operator, new_status_label: str):
    recipients = []
    if ticket.creator_id and ticket.creator_id != operator.id:
        recipients.append(ticket.creator)
    if ticket.assignee_id and ticket.assignee_id != operator.id:
        recipients.append(ticket.assignee)
    if not recipients:
        return None
    return notify(
        recipients,
        f"工单状态更新：{ticket.title}",
        f"状态已变更为「{new_status_label}」。",
        message_type="ticket",
        link="/tickets",
        sender=operator,
    )
