from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsersManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra):
        if not username:
            raise ValueError("用户名必填")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra)

    def create_superuser(self, username, email=None, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser 必须 is_staff=True")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser 必须 is_superuser=True")
        return self._create_user(username, email, password, **extra)


class Users(AbstractUser):
    """用户模型（扩展 Django AbstractUser）"""

    nickname = models.CharField(max_length=32, blank=True, default="", db_comment="用户昵称")
    email = models.EmailField(unique=True, blank=True, db_comment="电子邮件地址")
    phone = models.CharField(max_length=20, blank=True, null=True, db_comment="手机号")
    avatar = models.CharField(max_length=255, blank=True, null=True, db_comment="头像地址")
    password_changed_at = models.DateTimeField(null=True, blank=True, db_comment="密码修改时间")

    dept = models.ForeignKey(
        "Departments", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="users", db_comment="所属部门",
    )
    roles = models.ManyToManyField("Roles", related_name="users", blank=True)
    permissions = models.ManyToManyField("Permission", related_name="users", blank=True)

    last_login_ip = models.GenericIPAddressField(null=True, blank=True, db_comment="最后登录IP")
    last_login_time = models.DateTimeField(null=True, blank=True, db_comment="最后登录时间")

    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")
    updated_at = models.DateTimeField(auto_now=True, db_comment="更新时间")

    objects = UsersManager()

    class Meta:
        db_table = "nm_users"
        db_table_comment = "用户表"
        ordering = ("-id",)

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def __repr__(self):
        return f"<Users: {self.id} - {self.username}>"


class Roles(models.Model):
    ROLE_TYPES = (
        ("SYSTEM", "系统角色"),
        ("CUSTOM", "自定义角色"),
    )
    DATA_SCOPE_CHOICES = (
        ("ALL", "全部数据权限"),
        ("CUSTOM", "自定义数据权限"),
        ("DEPT", "本部门数据权限"),
        ("DEPT_AND_CHILD", "本部门及以下数据权限"),
        ("SELF", "仅本人数据权限"),
    )

    name = models.CharField(max_length=50, unique=True, db_comment="角色名称")
    code = models.CharField(max_length=50, unique=True, db_comment="角色标识码")
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES, default="CUSTOM", db_comment="角色类型")
    description = models.CharField(max_length=255, blank=True, default="", db_comment="角色描述")
    enable = models.BooleanField(default=True, db_comment="是否开启")
    data_scope = models.CharField(max_length=20, choices=DATA_SCOPE_CHOICES, default="SELF", db_comment="数据权限范围")

    menus = models.ManyToManyField("Menu", related_name="roles", blank=True)
    departments = models.ManyToManyField("Departments", related_name="roles", blank=True)
    permissions = models.ManyToManyField("Permission", related_name="roles", blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")
    updated_at = models.DateTimeField(auto_now=True, db_comment="更新时间")

    class Meta:
        db_table = "roles"
        db_table_comment = "角色表"

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Roles: {self.id} - {self.name}>"


class Departments(models.Model):
    name = models.CharField(max_length=50, db_comment="部门名称")
    code = models.CharField(max_length=50, unique=True, blank=True, db_comment="部门编码")
    sort = models.IntegerField(default=0, db_comment="排序")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        db_constraint=False, related_name="children", db_comment="上级部门",
    )
    owner = models.ForeignKey(
        "Users", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="owned_departments", db_comment="部门主管",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")
    updated_at = models.DateTimeField(auto_now=True, db_comment="更新时间")

    class Meta:
        db_table = "departments"
        db_table_comment = "部门表"
        ordering = ("sort", "-id")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Departments {self.id} - {self.name}>"


class Permission(models.Model):
    PERMISSION_TYPES = (
        ("MENU", "菜单权限"),
        ("OPERATION", "操作权限"),
        ("API", "API权限"),
    )

    name = models.CharField(max_length=25, unique=True, db_comment="权限名称")
    code = models.CharField(max_length=32, unique=True, db_comment="权限表示码")
    description = models.CharField(max_length=255, blank=True, default="", db_comment="权限描述")
    type = models.CharField(max_length=20, choices=PERMISSION_TYPES, default="OPERATION", db_comment="权限类型")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE,
        related_name="children", db_comment="父级权限",
    )
    api_path = models.CharField(max_length=255, null=True, blank=True, db_comment="API路径")
    method = models.CharField(max_length=20, null=True, blank=True, db_comment="HTTP方法")

    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")
    updated_at = models.DateTimeField(auto_now=True, db_comment="更新时间")

    class Meta:
        db_table = "permission"
        db_table_comment = "权限表"
        unique_together = [("api_path", "method")]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Permission: {self.id} - {self.name} - {self.code}>"


class Menu(models.Model):
    name = models.CharField(max_length=50, db_comment="菜单名称")
    path = models.CharField(max_length=255, blank=True, default="", db_comment="跳转路径")
    component = models.CharField(max_length=255, blank=True, default="", db_comment="前端组件")
    icon = models.CharField(max_length=100, blank=True, default="", db_comment="图标")
    sort = models.IntegerField(default=0, db_comment="排序")
    menu_type = models.CharField(max_length=50, default="menu", db_comment="菜单类型")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True,
        db_constraint=False, related_name="children", db_comment="上级菜单",
    )
    visible = models.BooleanField(default=True, db_comment="是否可见")
    permission = models.ForeignKey(
        "Permission", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="menus", db_comment="关联权限",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")
    updated_at = models.DateTimeField(auto_now=True, db_comment="更新时间")

    class Meta:
        db_table = "menu"
        db_table_comment = "菜单表"
        ordering = ("sort", "-id")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Menu: {self.id} - {self.path} - {self.menu_type}>"


class AuditLog(models.Model):
    """审计日志"""

    user = models.ForeignKey(
        "Users", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="audit_logs", db_comment="操作人",
    )
    action = models.CharField(max_length=64, db_comment="操作类型")
    resource_type = models.CharField(max_length=64, blank=True, default="", db_comment="资源类型")
    resource_id = models.CharField(max_length=64, blank=True, default="", db_comment="资源ID")
    before = models.JSONField(null=True, blank=True, db_comment="变更前")
    after = models.JSONField(null=True, blank=True, db_comment="变更后")
    ip = models.GenericIPAddressField(null=True, blank=True, db_comment="IP")
    user_agent = models.TextField(blank=True, default="", db_comment="User-Agent")
    created_at = models.DateTimeField(auto_now_add=True, db_comment="创建时间")

    class Meta:
        db_table = "audit_log"
        db_table_comment = "审计日志表"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.action} - {self.resource_type}:{self.resource_id}"

    def __repr__(self):
        return f"<AuditLog: {self.id} - {self.action}>"
