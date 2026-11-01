from rest_framework import serializers

from app.models.assets.assets import Asset
from app.models.tasks.task import ScanResult, Task, TaskLog


class AssetBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ["id", "name", "ip"]


class TaskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLog
        fields = ["id", "status", "start_time", "end_time", "duration", "result", "error_message", "created_at"]
        read_only_fields = fields


class ScanResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanResult
        fields = ["id", "raw_output", "parsed", "created_at"]
        read_only_fields = fields


class TaskSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source="creator.nickname", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    task_type_display = serializers.CharField(source="get_task_type_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)
    engine_display = serializers.CharField(source="get_engine_display", read_only=True)
    assets_detail = AssetBriefSerializer(source="assets", many=True, read_only=True)
    logs = TaskLogSerializer(many=True, read_only=True)
    scan_results = ScanResultSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "name", "description", "task_type", "task_type_display", "status",
            "status_display", "priority", "priority_display", "engine", "engine_display",
            "assets", "assets_detail", "targets", "target_type", "scan_config",
            "scan_ports", "schedule_type", "cron_expression", "progress",
            "result_summary", "error_message", "celery_task_id", "creator",
            "creator_name", "timeout", "created_at", "updated_at",
            "logs", "scan_results",
        ]
        read_only_fields = [
            "creator", "creator_name", "status", "status_display", "task_type_display",
            "priority_display", "engine_display", "progress", "result_summary",
            "error_message", "celery_task_id", "logs", "scan_results", "updated_at",
        ]
