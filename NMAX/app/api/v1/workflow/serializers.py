from rest_framework import serializers

from app.models.workflow.ticket import (
    TicketComment,
    TicketHistory,
    VulnerabilityTicket,
)
from app.services.state_machine import is_ticket_overdue


class TicketHistorySerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source="operator.nickname", read_only=True)

    class Meta:
        model = TicketHistory
        fields = [
            "id", "operator", "operator_name", "action",
            "old_status", "new_status", "comment", "created_at",
        ]
        read_only_fields = ["operator", "operator_name", "created_at"]


class TicketCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.nickname", read_only=True)

    class Meta:
        model = TicketComment
        fields = ["id", "author", "author_name", "content", "created_at"]
        read_only_fields = ["author", "author_name", "created_at"]


class VulnerabilityTicketSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.nickname", read_only=True)
    assignee_name = serializers.CharField(source="assignee.nickname", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    vuln_name = serializers.CharField(source="vulnerability.name", read_only=True)
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    is_overdue = serializers.SerializerMethodField()
    histories = TicketHistorySerializer(many=True, read_only=True)
    comments = TicketCommentSerializer(many=True, read_only=True)

    class Meta:
        model = VulnerabilityTicket
        fields = [
            "id", "title", "description", "priority", "status", "creator", "creator_name",
            "assignee", "assignee_name", "department", "department_name", "vulnerability",
            "vuln_name", "asset", "asset_name", "deadline", "closed_at", "resolution",
            "status_display", "priority_display", "is_overdue", "histories", "comments",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "creator", "creator_name", "assignee_name", "department_name",
            "status_display", "priority_display", "vuln_name", "asset_name",
            "is_overdue", "histories", "comments", "created_at", "updated_at",
            "closed_at",
        ]

    def get_is_overdue(self, obj) -> bool:
        return is_ticket_overdue(obj)


class TicketTransitionSerializer(serializers.Serializer):
    status = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True, default="")
    resolution = serializers.CharField(required=False, allow_blank=True, default="")
