from django.conf import settings
from rest_framework import serializers, viewsets
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.response import Response

from app.libs.permission.permission import HasPermission
from app.models.tasks.task import Task

from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = (HasPermission,)
    required_permissions = ["task:view"]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_queryset(self):
        user = self.request.user
        qs = Task.objects.all()
        if not user.is_superuser:
            qs = qs.filter(creator=user)
        params = self.request.query_params
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("engine"):
            qs = qs.filter(engine=params["engine"])
        if params.get("search"):
            qs = qs.filter(name__icontains=params["search"])
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        task = self.get_object()
        if task.status == "running":
            raise serializers.ValidationError({"detail": "任务正在执行中，请勿重复触发。"})
        if getattr(settings, "SCAN_EXECUTE_SYNC", False):
            from app.tasks import execute_scan
            execute_scan(task.id)
            task.refresh_from_db()
            return Response(self.get_serializer(task).data, status=http_status.HTTP_200_OK)

        from app.tasks import run_scan_task
        async_result = run_scan_task.delay(task.id)
        task.celery_task_id = async_result.id
        task.status = "running"
        task.save(update_fields=["celery_task_id", "status"])
        return Response(self.get_serializer(task).data, status=http_status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        task = self.get_object()
        if task.status in ("success", "failed", "canceled", "timeout"):
            raise serializers.ValidationError({"detail": "任务已结束，无法取消。"})
        task.status = "canceled"
        task.save(update_fields=["status"])
        return Response(self.get_serializer(task).data, status=http_status.HTTP_200_OK)
