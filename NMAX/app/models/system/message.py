from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    """站内消息模型
    
    用于存储和管理系统内部的消息通知，包括系统通知、工单通知、漏洞通知等
    """
    MESSAGE_TYPES = [
        ('system', '系统通知'),
        ('ticket', '工单通知'),
        ('vulnerability', '漏洞通知'),
        ('task', '任务通知'),
        ('other', '其他通知')
    ]
    
    PRIORITY_LEVELS = [
        ('high', '高'),
        ('medium', '中'),
        ('low', '低')
    ]
    
    # 消息基本信息
    title = models.CharField(
        max_length=200,
        verbose_name='消息标题',
        help_text='消息的标题'
    )
    content = models.TextField(
        verbose_name='消息内容',
        help_text='消息的详细内容'
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPES,
        default='system',
        verbose_name='消息类型',
        help_text='消息的分类类型'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_LEVELS,
        default='medium',
        verbose_name='优先级',
        help_text='消息的优先级别'
    )
    
    # 发送和接收信息
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='发送者',
        help_text='消息的发送者'
    )
    recipients = models.ManyToManyField(
        User,
        through='MessageRecipient',
        related_name='received_messages',
        verbose_name='接收者',
        help_text='消息的接收者列表'
    )
    
    # 时效性控制
    is_temporary = models.BooleanField(
        default=False,
        verbose_name='是否临时消息',
        help_text='标记消息是否为临时消息'
    )
    expiration_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='过期时间',
        help_text='消息的过期时间，为空表示永久有效'
    )
    
    # 创建和更新信息
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间',
        help_text='消息创建的时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='最后更新的时间'
    )
    
    class Meta:
        db_table = 'system_messages'
        db_table_comment = '站内消息表'
        verbose_name = '站内消息'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def __repr__(self):
        return f'<Message: {self.id} - {self.title}>'


class MessageRecipient(models.Model):
    """消息接收者关联模型
    
    用于管理消息的接收状态，包括已读/未读状态、阅读时间等
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name='关联消息',
        help_text='关联的消息对象'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='接收者',
        help_text='消息的接收者'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='是否已读',
        help_text='标记消息是否已被阅读'
    )
    read_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='阅读时间',
        help_text='消息被阅读的时间'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='是否删除',
        help_text='标记消息是否被接收者删除'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='记录创建的时间'
    )
    
    class Meta:
        db_table = 'system_message_recipients'
        db_table_comment = '消息接收状态表'
        verbose_name = '消息接收状态'
        verbose_name_plural = verbose_name
        unique_together = ['message', 'recipient']
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.recipient.username} - {self.message.title}'
    
    def __repr__(self):
        return f'<MessageRecipient: {self.message.id} - {self.recipient.username}>'