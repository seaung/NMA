from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.libs.permission.permission import HasPermission
from app.models.system.message import MessageRecipient

from .serializers import MessageRecipientSerializer


class MessageViewSet(viewsets.GenericViewSet):
    """站内消息：仅当前用户可见自己的消息。"""
    permission_classes = (HasPermission,)
    required_permissions = []
    serializer_class = MessageRecipientSerializer
    queryset = MessageRecipient.objects.all()

    def get_queryset(self):
        user = self.request.user
        qs = MessageRecipient.objects.filter(recipient=user, is_deleted=False)
        params = self.request.query_params
        if params.get("is_read") in ("true", "false"):
            qs = qs.filter(is_read=(params["is_read"] == "true"))
        if params.get("type"):
            qs = qs.filter(message__message_type=params["type"])
        return qs.select_related("message", "recipient")

    def list(self, request):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(
                MessageRecipientSerializer(page, many=True).data
            )
        return Response(MessageRecipientSerializer(qs, many=True).data)

    def retrieve(self, request, pk=None):
        obj = self.get_queryset().filter(pk=pk).first()
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(MessageRecipientSerializer(obj).data)

    def destroy(self, request, pk=None):
        obj = self.get_queryset().filter(pk=pk).first()
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        obj.is_deleted = True
        obj.save(update_fields=["is_deleted"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        obj = self.get_queryset().filter(pk=pk).first()
        if not obj:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if not obj.is_read:
            obj.is_read = True
            obj.read_time = timezone.now()
            obj.save(update_fields=["is_read", "read_time"])
        return Response({"id": obj.id, "is_read": True})

    @action(detail=False, methods=["post"])
    def read_all(self, request):
        updated = self.get_queryset().filter(is_read=False).update(
            is_read=True, read_time=timezone.now()
        )
        return Response({"updated": updated})

    @action(detail=False, methods=["get"])
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({"count": count})
