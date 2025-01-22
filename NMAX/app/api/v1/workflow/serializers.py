from rest_framework import serializers
from app.models.workflow.ticket import VulnerabilityTicket, TicketHistory, TicketComment


class VulnerabilityTicketSerializer(serializers.ModelSerializer):
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    assignee_username = serializers.CharField(source='assignee.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = VulnerabilityTicket
        fields = ['id', 'title', 'description', 'priority', 'status', 'creator', 'creator_username',
                 'assignee', 'assignee_username', 'created_at', 'updated_at', 'deadline',
                 'resolution', 'status_display', 'priority_display']
        read_only_fields = ['creator', 'creator_username', 'assignee_username', 'status_display',
                          'priority_display', 'created_at', 'updated_at']


class TicketHistorySerializer(serializers.ModelSerializer):
    operator_username = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = TicketHistory
        fields = ['id', 'ticket', 'operator', 'operator_username', 'action',
                 'old_status', 'new_status', 'comment', 'created_at']
        read_only_fields = ['operator', 'operator_username', 'created_at']


class TicketCommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = TicketComment
        fields = ['id', 'ticket', 'author', 'author_username', 'content', 'created_at']
        read_only_fields = ['author', 'author_username', 'created_at']