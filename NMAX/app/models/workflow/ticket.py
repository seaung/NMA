from django.conf import settings
from django.db import models
from django.utils import timezone


class VulnerabilityTicket(models.Model):
    PRIORITY_CHOICES = [
        ("critical", "严重"),
        ("high", "高"),
        ("medium", "中"),
        ("low", "低"),
    ]

    STATUS_CHOICES = [
        ("created", "已创建"),
        ("assigned", "已分配"),
        ("processing", "处理中"),
        ("pending_verify", "待验证"),
        ("resolved", "已解决"),
        ("closed", "已关闭"),
        ("rejected", "已拒绝"),
        ("reopened", "重新打开"),
    ]

    title = models.CharField("标题", max_length=200, db_comment="标题")
    description = models.TextField("描述", blank=True, default="", db_comment="描述")
    priority = models.CharField("优先级", max_length=20, choices=PRIORITY_CHOICES, default="medium", db_comment="优先级")
    status = models.CharField("状态", max_length=20, choices=STATUS_CHOICES, default="created", db_comment="状态")

    vulnerability = models.ForeignKey(
        "app.Vulnerability", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets", db_comment="关联漏洞",
    )
    asset = models.ForeignKey(
        "app.Asset", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets", db_comment="关联资产",
    )
    department = models.ForeignKey(
        "app.Departments", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets", db_comment="处理部门",
    )

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tickets", verbose_name="创建人")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_tickets", verbose_name="处理人",
    )
    created_at = models.DateTimeField("创建时间", default=timezone.now, db_comment="创建时间")
    updated_at = models.DateTimeField("更新时间", auto_now=True, db_comment="更新时间")
    deadline = models.DateTimeField("截止时间", null=True, blank=True, db_comment="SLA截止时间")
    closed_at = models.DateTimeField("关闭时间", null=True, blank=True, db_comment="关闭时间")
    resolution = models.TextField("解决方案", null=True, blank=True, db_comment="解决方案")

    class Meta:
        verbose_name = "漏洞工单"
        verbose_name_plural = verbose_name
        db_table = "vulnerability_tickets"
        db_table_comment = "漏洞工单表"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<VulnerabilityTicket: {self.id} - {self.title}>"


class TicketHistory(models.Model):
    ticket = models.ForeignKey(VulnerabilityTicket, on_delete=models.CASCADE, related_name="histories", verbose_name="工单")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="操作人")
    action = models.CharField("操作", max_length=50, db_comment="操作")
    old_status = models.CharField("原状态", max_length=20, null=True, blank=True, db_comment="原状态")
    new_status = models.CharField("新状态", max_length=20, null=True, blank=True, db_comment="新状态")
    comment = models.TextField("备注", null=True, blank=True, db_comment="备注")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        verbose_name = "工单历史"
        verbose_name_plural = verbose_name
        db_table = "ticket_history"
        db_table_comment = "工单历史表"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_id} - {self.action}"

    def __repr__(self):
        return f"<TicketHistory: {self.id}>"


class TicketComment(models.Model):
    ticket = models.ForeignKey(VulnerabilityTicket, on_delete=models.CASCADE, related_name="comments", verbose_name="工单")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="评论人")
    content = models.TextField("内容", db_comment="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")

    class Meta:
        verbose_name = "工单评论"
        verbose_name_plural = verbose_name
        db_table = "ticket_comment"
        db_table_comment = "工单评论表"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_id} - {self.author_id}"

    def __repr__(self):
        return f"<TicketComment: {self.id}>"
