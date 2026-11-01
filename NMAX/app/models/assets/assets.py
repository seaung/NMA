from django.db import models
from django.utils import timezone


class Asset(models.Model):
    """资产模型（合并主机/Web/域名/网络资产，聚焦暴露面管理）"""

    STATUS_CHOICES = (
        ("in_use", "使用中"),
        ("idle", "闲置"),
        ("maintenance", "维护中"),
        ("scrapped", "已报废"),
    )
    TYPE_CHOICES = (
        ("host", "主机"),
        ("web", "Web应用"),
        ("domain", "域名"),
        ("network", "网络设备"),
        ("database", "数据库"),
        ("other", "其他"),
    )
    SECURITY_LEVEL_CHOICES = (
        ("critical", "严重"),
        ("high", "高危"),
        ("medium", "中危"),
        ("low", "低危"),
        ("info", "信息"),
    )
    IMPORTANCE_CHOICES = (
        (1, "低"),
        (2, "中"),
        (3, "高"),
        (4, "核心"),
    )

    name = models.CharField("资产名称", max_length=100, db_comment="资产名称")
    ip = models.CharField("资产IP", max_length=255, blank=True, default="", db_comment="资产IP")
    hostname = models.CharField("主机名", max_length=255, blank=True, default="", db_comment="主机名")
    domain = models.CharField("域名", max_length=255, blank=True, default="", db_comment="关联域名")
    ports = models.JSONField("开放端口", default=list, blank=True, db_comment="开放端口列表")
    web_url = models.URLField("Web地址", blank=True, default="", db_comment="Web访问地址")
    service_fingerprint = models.CharField("服务指纹", max_length=255, blank=True, default="", db_comment="服务指纹(用于去重/识别)")
    exposed = models.BooleanField("是否暴露", default=False, db_comment="是否暴露于公网")
    asset_group = models.CharField("资产分组", max_length=100, blank=True, default="", db_comment="资产分组")

    asset_type = models.CharField("资产类型", max_length=20, choices=TYPE_CHOICES, default="host")
    asset_status = models.CharField("资产状态", max_length=20, choices=STATUS_CHOICES, default="idle")
    area = models.CharField("所在区域", max_length=50, blank=True, default="", db_comment="资产位置")
    importance = models.IntegerField("重要程度", choices=IMPORTANCE_CHOICES, default=1, db_comment="重要程度(风险评分权重)")
    security_level = models.CharField("安全等级", max_length=20, choices=SECURITY_LEVEL_CHOICES, null=True, blank=True, db_comment="安全等级")

    manager = models.ForeignKey("app.Users", on_delete=models.SET_NULL, null=True, blank=True, related_name="managed_assets", verbose_name="负责人")
    department = models.ForeignKey("app.Departments", on_delete=models.SET_NULL, null=True, blank=True, related_name="assets", verbose_name="所属部门")
    business_system = models.CharField("业务系统", max_length=100, blank=True, default="", db_comment="所属业务系统")

    os_type = models.CharField("操作系统类型", max_length=50, blank=True, default="", db_comment="操作系统类型")
    os_version = models.CharField("操作系统版本", max_length=50, blank=True, default="", db_comment="操作系统版本")
    kernel_version = models.CharField("内核版本", max_length=50, blank=True, null=True, db_comment="内核版本")
    mac_address = models.CharField("MAC地址", max_length=17, blank=True, default="", db_comment="MAC地址")
    dns_server = models.CharField("DNS服务器", max_length=255, blank=True, default="", db_comment="DNS服务器")
    gateway = models.CharField("网关地址", max_length=255, blank=True, default="", db_comment="网关地址")
    cpu_model = models.CharField("CPU型号", max_length=100, blank=True, default="", db_comment="CPU型号")
    cpu_cores = models.IntegerField("CPU核心数", null=True, blank=True, db_comment="CPU核心数")
    memory_size = models.IntegerField("内存大小(GB)", null=True, blank=True, db_comment="内存大小")
    disk_size = models.IntegerField("磁盘大小(GB)", null=True, blank=True, db_comment="磁盘大小")
    is_hardened = models.BooleanField("是否已加固", default=False, db_comment="是否已加固")

    tags = models.JSONField("标签", default=list, blank=True, db_comment="标签")
    description = models.TextField("描述", blank=True, default="", db_comment="描述")
    last_scan_time = models.DateTimeField("最后扫描时间", null=True, blank=True, db_comment="最后扫描时间")

    created_by = models.ForeignKey("app.Users", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_assets", verbose_name="创建人")
    created_at = models.DateTimeField("创建时间", default=timezone.now, db_comment="创建时间")
    updated_at = models.DateTimeField("更新时间", auto_now=True, db_comment="更新时间")

    is_deleted = models.BooleanField("是否删除", default=False, db_comment="软删除标记")
    deleted_at = models.DateTimeField("删除时间", null=True, blank=True, db_comment="删除时间")

    class Meta:
        verbose_name = "资产"
        verbose_name_plural = verbose_name
        db_table = "assets"
        db_table_comment = "资产表"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ip"], name="idx_asset_ip"),
            models.Index(fields=["asset_type"], name="idx_asset_type"),
            models.Index(fields=["department"], name="idx_asset_dept"),
            models.Index(fields=["security_level"], name="idx_asset_seclevel"),
            models.Index(fields=["is_deleted"], name="idx_asset_deleted"),
        ]

    def __str__(self):
        return self.name
