from rest_framework import serializers

from app.models.system.message import Message, MessageRecipient


class MessageRecipientSerializer(serializers.ModelSerializer):
    """扁平化消息 + 接收状态，便于前端直接渲染。"""
    message_id = serializers.IntegerField(source="message.id", read_only=True)
    title = serializers.CharField(source="message.title", read_only=True)
    content = serializers.CharField(source="message.content", read_only=True)
    message_type = serializers.CharField(source="message.message_type", read_only=True)
    priority = serializers.CharField(source="message.priority", read_only=True)
    level = serializers.CharField(source="message.level", read_only=True)
    link = serializers.CharField(source="message.link", read_only=True)
    message_created_at = serializers.DateTimeField(
        source="message.created_at", read_only=True
    )

    class Meta:
        model = MessageRecipient
        fields = [
            "id", "message_id", "title", "content", "message_type", "priority",
            "level", "link", "message_created_at", "is_read", "read_time",
        ]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id", "title", "content", "message_type", "priority", "level",
            "link", "sender", "created_at", "updated_at",
        ]
