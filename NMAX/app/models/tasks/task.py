from django.conf import settings
from django.db import models


class Task(models.Model):
    """扫描/任务模型"""

    TASK_TYPES = (
        ("immediate", "即时任务"),
        ("scheduled", "定时任务"),
        ("periodic", "周期任务"),
        ("scan", "扫描任务"),
    )
    TARGET_TYPES = (
        ("ip", "IP地址"),
        ("domain", "域名"),
        ("url", "URL"),
        ("subnet", "子网"),
    )
    SCHEDULE_TYPES = (
        ("once", "单次"),
        ("cron", "Cron"),
        ("interval", "间隔"),
    )
    ENGINE_CHOICES = (
        ("nmap", "Nmap"),
        ("nessus", "Nessus"),
        ("awvs", "AWVS"),
        ("custom", "自定义"),
    )
    TASK_STATUS = (
        ("pending", "等待执行"),
        ("running", "执行中"),
        ("success", "执行成功"),
        ("failed", "执行失败"),
        ("timeout", "执行超时"),
        ("canceled", "已取消"),
    )
    PRIORITY_LEVELS = (
        ("high", "高"),
        ("medium", "中"),
        ("low", "低"),
    )

    name = models.CharField("任务名称", max_length=100, db_comment="任务名称")
    description = models.TextField("任务描述", null=True, blank=True, db_comment="任务描述")
    task_type = models.CharField("任务类型", max_length=20, choices=TASK_TYPES, default="scan", db_comment="任务类型")
    status = models.CharField("任务状态", max_length=20, choices=TASK_STATUS, default="pending", db_comment="任务状态")
    priority = models.CharField("优先级", max_length=10, choices=PRIORITY_LEVELS, default="medium", db_comment="优先级")

    engine = models.CharField("扫描引擎", max_length=20, choices=ENGINE_CHOICES, default="nmap", db_comment="扫描引擎")
    assets = models.ManyToManyField("app.Asset", blank=True, related_name="tasks")
    targets = models.JSONField("扫描目标", default=list, blank=True, db_comment="扫描目标(域名/URL/子网)")
    target = models.TextField("原始目标", null=True, blank=True, db_comment="扫描目标(原始文本)")
    target_type = models.CharField("目标类型", max_length=20, choices=TARGET_TYPES, null=True, blank=True, db_comment="目标类型")
    scan_config = models.JSONField("扫描配置", default=dict, blank=True, db_comment="扫描配置")
    scan_depth = models.IntegerField("扫描深度", default=3, null=True, blank=True, db_comment="扫描深度")
    concurrent_num = models.IntegerField("并发数", default=10, null=True, blank=True, db_comment="并发数")
    scan_ports = models.CharField("扫描端口", max_length=255, null=True, blank=True, db_comment="扫描端口范围")
    exclude_targets = models.TextField("排除目标", null=True, blank=True, db_comment="排除目标")

    schedule_type = models.CharField("调度类型", max_length=20, choices=SCHEDULE_TYPES, default="once", db_comment="调度类型")
    cron_expression = models.CharField("Cron表达式", max_length=100, null=True, blank=True, db_comment="Cron表达式")
    interval_seconds = models.IntegerField("间隔(秒)", null=True, blank=True, db_comment="执行间隔(秒)")
    planned_start_time = models.DateTimeField("计划开始时间", null=True, blank=True, db_comment="计划开始时间")

    celery_task_id = models.CharField("Celery任务ID", max_length=255, null=True, blank=True, db_comment="Celery任务ID")
    progress = models.IntegerField("进度", default=0, db_comment="执行进度(0-100)")
    result_summary = models.TextField("结果摘要", blank=True, default="", db_comment="执行结果摘要")
    timeout = models.IntegerField("超时(秒)", default=3600, db_comment="超时时间")
    max_retries = models.IntegerField("最大重试", default=3, db_comment="最大重试次数")
    retry_count = models.IntegerField("当前重试", default=0, db_comment="当前重试次数")

    actual_start_time = models.DateTimeField("实际开始时间", null=True, blank=True, db_comment="实际开始时间")
    completed_time = models.DateTimeField("完成时间", null=True, blank=True, db_comment="完成时间")
    result = models.TextField("执行结果", null=True, blank=True, db_comment="执行结果")
    error_message = models.TextField("错误信息", null=True, blank=True, db_comment="错误信息")

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks", db_comment="创建人")
    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")
    updated_at = models.DateTimeField(auto_now=True, db_comment="更新时间")

    class Meta:
        db_table = "tasks"
        db_table_comment = "任务管理"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Task: {self.id} - {self.name}>"


class TaskLog(models.Model):
    """任务执行日志"""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="logs", db_comment="关联任务")
    status = models.CharField("执行状态", max_length=20, choices=Task.TASK_STATUS, db_comment="执行状态")
    start_time = models.DateTimeField("开始时间", db_comment="开始时间")
    end_time = models.DateTimeField("结束时间", null=True, blank=True, db_comment="结束时间")
    duration = models.IntegerField("时长(秒)", null=True, blank=True, db_comment="执行时长")
    result = models.TextField("执行结果", null=True, blank=True, db_comment="执行结果")
    error_message = models.TextField("错误信息", null=True, blank=True, db_comment="错误信息")
    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")

    class Meta:
        db_table = "task_logs"
        db_table_comment = "任务执行日志"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.task.name} - {self.status}"

    def __repr__(self):
        return f"<TaskLog: {self.id} - {self.task.name}>"


class ScanResult(models.Model):
    """原始扫描结果（用于追溯与去重解析）"""

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="scan_results", db_comment="关联任务")
    raw_output = models.TextField("原始输出", blank=True, default="", db_comment="原始扫描输出")
    parsed = models.JSONField("解析结果", null=True, blank=True, db_comment="解析后的漏洞发现列表")
    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")

    class Meta:
        db_table = "scan_results"
        db_table_comment = "扫描结果表"
        ordering = ["-created_at"]

    def __str__(self):
        return f"ScanResult#{self.id} task={self.task_id}"

    def __repr__(self):
        return f"<ScanResult: {self.id}>"
