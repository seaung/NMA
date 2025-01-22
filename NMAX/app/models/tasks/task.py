from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Task(models.Model):
    """任务基类，包含共同的字段"""
    TASK_TYPES = (
        ('immediate', '即时任务'),
        ('scheduled', '定时任务'),
        ('periodic', '周期任务'),
        ('scan', '扫描任务')
    )
    
    TARGET_TYPES = (
        ('ip', 'IP地址'),
        ('domain', '域名'),
        ('url', 'URL'),
        ('subnet', '子网')
    )

    TASK_STATUS = (
        ('pending', '等待执行'),
        ('running', '执行中'),
        ('success', '执行成功'),
        ('failed', '执行失败'),
        ('timeout', '执行超时'),
        ('canceled', '已取消')
    )

    PRIORITY_LEVELS = (
        ('high', '高'),
        ('medium', '中'),
        ('low', '低')
    )

    name = models.CharField(max_length=100, db_column='name', db_comment='任务名称')
    description = models.TextField(null=True, blank=True, db_column='description', db_comment='任务描述')
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, db_column='task_type', db_comment='任务类型')
    status = models.CharField(max_length=20, choices=TASK_STATUS, default='pending', db_column='status', db_comment='任务状态')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', db_column='priority', db_comment='优先级')
    
    # 任务配置
    celery_task_id = models.CharField(max_length=255, null=True, blank=True, db_column='celery_task_id', db_comment='Celery任务ID')
    timeout = models.IntegerField(default=3600, db_column='timeout', db_comment='超时时间(秒)')
    max_retries = models.IntegerField(default=3, db_column='max_retries', db_comment='最大重试次数')
    retry_count = models.IntegerField(default=0, db_column='retry_count', db_comment='当前重试次数')
    
    # 扫描任务配置
    target = models.TextField(null=True, blank=True, db_column='target', db_comment='扫描目标')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES, null=True, blank=True, db_column='target_type', db_comment='目标类型')
    scan_depth = models.IntegerField(default=3, null=True, blank=True, db_column='scan_depth', db_comment='扫描深度')
    concurrent_num = models.IntegerField(default=10, null=True, blank=True, db_column='concurrent_num', db_comment='并发数')
    scan_ports = models.CharField(max_length=255, null=True, blank=True, db_column='scan_ports', db_comment='扫描端口范围')
    exclude_targets = models.TextField(null=True, blank=True, db_column='exclude_targets', db_comment='排除目标')
    asset_id = models.IntegerField(null=True, blank=True, db_column='asset_id', db_comment='关联资产ID')
    
    # 执行计划
    planned_start_time = models.DateTimeField(null=True, blank=True, db_column='planned_start_time', db_comment='计划开始时间')
    cron_expression = models.CharField(max_length=100, null=True, blank=True, db_column='cron_expression', db_comment='Cron表达式')
    interval_seconds = models.IntegerField(null=True, blank=True, db_column='interval_seconds', db_comment='执行间隔(秒)')
    
    # 执行信息
    actual_start_time = models.DateTimeField(null=True, blank=True, db_column='actual_start_time', db_comment='实际开始时间')
    completed_time = models.DateTimeField(null=True, blank=True, db_column='completed_time', db_comment='完成时间')
    result = models.TextField(null=True, blank=True, db_column='result', db_comment='执行结果')
    error_message = models.TextField(null=True, blank=True, db_column='error_message', db_comment='错误信息')
    
    # 创建和更新信息
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', db_column='creator', db_comment='创建人')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', db_comment='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_column='updated_at', db_comment='更新时间')

    class Meta:
        db_table = 'tasks'
        db_table_comment = '任务管理'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Task: {self.id} - {self.name}>'


class TaskLog(models.Model):
    """任务执行日志"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='logs', db_column='task_id', db_comment='关联任务')
    status = models.CharField(max_length=20, choices=Task.TASK_STATUS, db_column='status', db_comment='执行状态')
    start_time = models.DateTimeField(db_column='start_time', db_comment='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, db_column='end_time', db_comment='结束时间')
    duration = models.IntegerField(null=True, blank=True, db_column='duration', db_comment='执行时长(秒)')
    result = models.TextField(null=True, blank=True, db_column='result', db_comment='执行结果')
    error_message = models.TextField(null=True, blank=True, db_column='error_message', db_comment='错误信息')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', db_comment='创建时间')

    class Meta:
        db_table = 'task_logs'
        db_table_comment = '任务执行日志'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.task.name} - {self.status}'

    def __repr__(self) -> str:
        return f'<TaskLog: {self.id} - {self.task.name}>'