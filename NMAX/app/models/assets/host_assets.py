from django.db import models


class HostAssets(models.Model):
    # 基本信息
    name = models.CharField(db_column='name', db_comment='资产名称', max_length=32)
    ip = models.CharField(db_column='ip', db_comment='资产IP', max_length=255)
    area = models.CharField(db_column='area', db_comment='资产位置', max_length=50)
    manager = models.CharField(db_column='manager', db_comment='资产管理人', max_length=50)
    asset_type = models.CharField(db_column='asset_type', db_comment='资产类型', max_length=50)
    asset_status = models.CharField(db_column='asset_status', db_comment='资产状态', max_length=20)
    
    # 系统信息
    os_type = models.CharField(db_column='os_type', db_comment='操作系统类型', max_length=50)
    os_version = models.CharField(db_column='os_version', db_comment='操作系统版本', max_length=50)
    kernel_version = models.CharField(db_column='kernel_version', db_comment='内核版本', max_length=50, null=True, blank=True)
    
    # 网络配置
    mac_address = models.CharField(db_column='mac_address', db_comment='MAC地址', max_length=17, null=True, blank=True)
    dns_server = models.CharField(db_column='dns_server', db_comment='DNS服务器', max_length=255, null=True, blank=True)
    gateway = models.CharField(db_column='gateway', db_comment='网关地址', max_length=255, null=True, blank=True)
    
    # 硬件信息
    cpu_model = models.CharField(db_column='cpu_model', db_comment='CPU型号', max_length=100, null=True, blank=True)
    cpu_cores = models.IntegerField(db_column='cpu_cores', db_comment='CPU核心数', null=True, blank=True)
    memory_size = models.IntegerField(db_column='memory_size', db_comment='内存大小(GB)', null=True, blank=True)
    disk_size = models.IntegerField(db_column='disk_size', db_comment='磁盘大小(GB)', null=True, blank=True)
    
    # 安全信息
    is_hardened = models.BooleanField(db_column='is_hardened', db_comment='是否已加固', default=False)
    last_scan_time = models.DateTimeField(db_column='last_scan_time', db_comment='最后扫描时间', null=True, blank=True)
    security_level = models.CharField(db_column='security_level', db_comment='安全等级', max_length=20, null=True, blank=True)
    
    # 标签和备注
    tags = models.CharField(db_column='tags', db_comment='资产标签', max_length=255, null=True, blank=True)
    description = models.TextField(db_column='description', db_comment='资产描述', null=True, blank=True)
    
    # 时间信息
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

