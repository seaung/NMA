from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from app.libs.permission.data_scope import get_data_scope
from app.libs.permission.permission import HasPermission
from app.models.users.users import Users
from app.models.workflow.ticket import (
    TicketComment,
    TicketHistory,
    VulnerabilityTicket,
)
from app.services.notification import notify_ticket_assigned, notify_ticket_status
from app.services.state_machine import (
    TICKET_STATUS_LABELS,
    compute_ticket_deadline,
    transition_ticket,
)

from .serializers import (
    TicketCommentSerializer,
    VulnerabilityTicketSerializer,
)


class VulnerabilityTicketViewSet(viewsets.ModelViewSet):
    permission_classes = (HasPermission,)
    required_permissions = ["ticket:view"]
    serializer_class = VulnerabilityTicketSerializer
    queryset = VulnerabilityTicket.objects.all()

    def get_queryset(self):
        user = self.request.user
        is_all, dept_ids = get_data_scope(user)
        if is_all:
            qs = VulnerabilityTicket.objects.all()
        elif dept_ids:
            qs = VulnerabilityTicket.objects.filter(department_id__in=list(dept_ids))
        else:
            qs = VulnerabilityTicket.objects.filter(creator=user) | \
                VulnerabilityTicket.objects.filter(assignee=user)

        params = self.request.query_params
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("priority"):
            qs = qs.filter(priority=params["priority"])
        if params.get("assignee"):
            qs = qs.filter(assignee_id=params["assignee"])
        if params.get("search"):
            qs = qs.filter(title__icontains=params["search"])
        if params.get("is_overdue") == "true":
            qs = qs.filter(deadline__lt=timezone.now()).exclude(
                status__in=["resolved", "closed"]
            )
        return qs.distinct()

    def perform_create(self, serializer):
        ticket = serializer.save(creator=self.request.user)
        if not ticket.department_id and self.request.user.dept_id:
            ticket.department_id = self.request.user.dept_id
            ticket.save(update_fields=["department"])
        TicketHistory.objects.create(
            ticket=ticket, operator=self.request.user, action="create",
            new_status=ticket.status, comment="创建工单",
        )
        if ticket.assignee_id and ticket.assignee_id != self.request.user.id:
            notify_ticket_assigned(ticket, ticket.assignee, self.request.user)

    @action(detail=True, methods=["post"])
    def assign(self, request: Request, pk=None) -> Response:
        ticket = self.get_object()
        assignee_id = request.data.get("assignee_id")
        if not assignee_id:
            raise serializers.ValidationError({"assignee_id": "处理人不能为空"})
        try:
            assignee = Users.objects.get(id=assignee_id)
        except Users.DoesNotExist:
            raise serializers.ValidationError({"assignee_id": "处理人不存在"})

        old_status = ticket.status
        ticket.assignee = assignee
        if ticket.status == "created":
            ticket.status = "assigned"
        if not ticket.deadline:
            ticket.deadline = compute_ticket_deadline(ticket.priority)
        ticket.save()
        TicketHistory.objects.create(
            ticket=ticket, operator=request.user, action="assign",
            old_status=old_status, new_status=ticket.status,
            comment=f"分配给 {assignee.nickname or assignee.username}",
        )
        notify_ticket_assigned(ticket, assignee, request.user)
        return Response(self.get_serializer(ticket).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def change_status(self, request: Request, pk=None) -> Response:
        ticket = self.get_object()
        new_status = request.data.get("status")
        note = request.data.get("note", "")
        resolution = request.data.get("resolution", "")
        if not new_status:
            raise serializers.ValidationError({"status": "状态不能为空"})
        try:
            transition_ticket(
                ticket, new_status, request.user,
                note=note, resolution=resolution or None,
            )
        except ValueError as e:
            raise serializers.ValidationError({"status": str(e)})

        notify_ticket_status(
            ticket, request.user, TICKET_STATUS_LABELS.get(new_status, new_status)
        )
        return Response(self.get_serializer(ticket).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def add_comment(self, request: Request, pk=None) -> Response:
        ticket = self.get_object()
        content = (request.data.get("content") or "").strip()
        if not content:
            raise serializers.ValidationError({"content": "评论内容不能为空"})
        TicketComment.objects.create(
            ticket=ticket, author=request.user, content=content
        )
        return Response(
            TicketCommentSerializer(
                ticket.comments.all().order_by("-created_at"), many=True
            ).data,
            status=status.HTTP_201_CREATED,
        )
