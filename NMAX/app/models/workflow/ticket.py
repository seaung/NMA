from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class VulnerabilityTicket(models.Model):
    PRIORITY_CHOICES = [
        ('critical', '严重'),
        ('high', '高'),
        ('medium', '中'),
        ('low', '低'),
    ]

    STATUS_CHOICES = [
        ('created', '已创建'),
        ('assigned', '已分配'),
        ('processing', '处理中'),
        ('verifying', '待验证'),
        ('resolved', '已解决'),
        ('closed', '已关闭'),
        ('rejected', '已拒绝'),
    ]

    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name='状态')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets', verbose_name='创建人')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets', verbose_name='处理人')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='截止时间')
    resolution = models.TextField(null=True, blank=True, verbose_name='解决方案')

    class Meta:
        verbose_name = '漏洞工单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class TicketHistory(models.Model):
    ticket = models.ForeignKey(VulnerabilityTicket, on_delete=models.CASCADE, related_name='histories', verbose_name='工单')
    operator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='操作人')
    action = models.CharField(max_length=50, verbose_name='操作')
    old_status = models.CharField(max_length=20, null=True, blank=True, verbose_name='原状态')
    new_status = models.CharField(max_length=20, null=True, blank=True, verbose_name='新状态')
    comment = models.TextField(null=True, blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '工单历史'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class TicketComment(models.Model):
    ticket = models.ForeignKey(VulnerabilityTicket, on_delete=models.CASCADE, related_name='comments', verbose_name='工单')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论人')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')

    class Meta:
        verbose_name = '工单评论'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']