from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class SystemConfig(models.Model):
    """系统配置模型
    
    用于存储和管理系统全局配置信息，包括用户登录相关设置和其他系统配置项
    """
    # 登录相关配置
    session_timeout = models.IntegerField(
        verbose_name='登录会话时长',
        help_text='用户登录会话的有效期（分钟）',
        default=30,
        validators=[MinValueValidator(5)]
    )
    max_login_attempts = models.IntegerField(
        verbose_name='最大登录尝试次数',
        help_text='用户登录失败的最大尝试次数，超过后账户将被锁定',
        default=5,
        validators=[MinValueValidator(1)]
    )
    account_lockout_duration = models.IntegerField(
        verbose_name='账户锁定时长',
        help_text='账户被锁定的持续时间（分钟）',
        default=30,
        validators=[MinValueValidator(1)]
    )
    password_expiration_days = models.IntegerField(
        verbose_name='密码有效期',
        help_text='用户密码的有效天数，超过后需要修改密码',
        default=90,
        validators=[MinValueValidator(1)]
    )
    
    # 通用配置项
    key = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='配置项键名',
        help_text='配置项的唯一标识符'
    )
    value = models.TextField(
        verbose_name='配置项值',
        help_text='配置项的值'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='配置说明',
        help_text='配置项的描述信息'
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name='是否系统配置',
        help_text='标记是否为系统内置的配置项'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'system_config'
        db_table_comment = '系统配置表'
        verbose_name = '系统配置'
        verbose_name_plural = verbose_name
        ordering = ['key']

    def __str__(self):
        return f'{self.key}: {self.value}'

    def __repr__(self):
        return f'<SystemConfig: {self.key}>'