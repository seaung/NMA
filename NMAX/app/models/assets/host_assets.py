from django.db import models


class HostAssets(models.Model):
    name = models.CharField(db_column='name', db_comment='资产名称', max_length=32)
    ip = models.CharField(db_column='ip', db_comment='资产IP', max_length=255)
    area = models.CharField(db_column='area', db_comment='资产位置', max_length=50)
    manager = models.CharField(db_column='manager', db_comment='资产管理人', max_length=50)
    created_at = models.DateTimeField(db_column='created_at', db_comment='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='updated_at', db_comment='更新时间', auto_now=True)

    class Meta:
        db_table = 'host_assets'
        db_table_comment = '主机资产'
        ordering = ('-id', )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<HostAssets : {self.id} - {self.name}>'

