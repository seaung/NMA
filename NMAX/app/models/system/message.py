from django.conf import settings
from django.db import models
from django.utils import timezone


class Message(models.Model):
    """站内消息模型"""

    MESSAGE_TYPES = [
        ("system", "系统通知"),
        ("ticket", "工单通知"),
        ("vulnerability", "漏洞通知"),
        ("task", "任务通知"),
        ("overdue", "逾期提醒"),
        ("other", "其他通知"),
    ]
    PRIORITY_LEVELS = [
        ("high", "高"),
        ("medium", "中"),
        ("low", "低"),
    ]
    LEVEL_CHOICES = [
        ("info", "普通"),
        ("warning", "警告"),
        ("danger", "严重"),
    ]

    title = models.CharField("消息标题", max_length=200, db_comment="消息标题")
    content = models.TextField("消息内容", db_comment="消息内容")
    message_type = models.CharField("消息类型", max_length=20, choices=MESSAGE_TYPES, default="system", db_comment="消息类型")
    priority = models.CharField("优先级", max_length=10, choices=PRIORITY_LEVELS, default="medium", db_comment="优先级")
    level = models.CharField("级别", max_length=10, choices=LEVEL_CHOICES, default="info", db_comment="消息级别")

    link = models.URLField("跳转链接", blank=True, default="", db_comment="相关链接")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sent_messages", verbose_name="发送者", db_comment="系统消息可为空",
    )
    recipients = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="MessageRecipient", related_name="received_messages",
        verbose_name="接收者",
    )

    is_temporary = models.BooleanField("是否临时", default=False, db_comment="是否临时消息")
    expires_at = models.DateTimeField("过期时间", null=True, blank=True, db_comment="过期时间，为空表示永久")

    created_at = models.DateTimeField("创建时间", default=timezone.now, db_comment="创建时间")
    updated_at = models.DateTimeField("更新时间", auto_now=True, db_comment="更新时间")

    class Meta:
        db_table = "messages"
        db_table_comment = "站内消息表"
        verbose_name = "站内消息"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Message: {self.id} - {self.title}>"


class MessageRecipient(models.Model):
    """消息接收者关联（已读/删除状态）"""

    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="关联消息", db_comment="关联消息")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="接收者", db_comment="接收者")
    is_read = models.BooleanField("是否已读", default=False, db_comment="是否已读")
    read_time = models.DateTimeField("阅读时间", null=True, blank=True, db_comment="阅读时间")
    is_deleted = models.BooleanField("是否删除", default=False, db_comment="是否删除")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", db_comment="创建时间")

    class Meta:
        db_table = "message_recipients"
        db_table_comment = "消息接收状态表"
        verbose_name = "消息接收状态"
        verbose_name_plural = verbose_name
        unique_together = ["message", "recipient"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.username} - {self.message.title}"

    def __repr__(self):
        return f"<MessageRecipient: {self.message.id} - {self.recipient.username}>"
