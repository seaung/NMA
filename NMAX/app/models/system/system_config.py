from django.db import models
from django.utils import timezone


class SystemConfig(models.Model):
    """系统配置（纯 key-value，系统默认 + DB 覆盖）"""

    key = models.CharField("配置键", max_length=64, unique=True, db_comment="配置项键名")
    value = models.JSONField("配置值", null=True, blank=True, db_comment="配置项值(支持任意JSON)")
    description = models.CharField("配置说明", max_length=255, blank=True, default="", db_comment="配置说明")
    is_system = models.BooleanField("是否系统配置", default=False, db_comment="是否系统内置配置")
    created_at = models.DateTimeField("创建时间", default=timezone.now, db_comment="创建时间")
    updated_at = models.DateTimeField("更新时间", auto_now=True, db_comment="更新时间")

    class Meta:
        db_table = "system_config"
        db_table_comment = "系统配置表"
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name
        ordering = ["key"]

    def __str__(self):
        return f"{self.key}: {self.value}"

    def __repr__(self):
        return f"<SystemConfig: {self.key}>"

    @classmethod
    def get_value(cls, key, default=None):
        obj = cls.objects.filter(key=key).first()
        return obj.value if obj else default

    @classmethod
    def set_value(cls, key, value, description="", is_system=False):
        obj, _ = cls.objects.update_or_create(
            key=key,
            defaults={"value": value, "description": description, "is_system": is_system},
        )
        return obj
