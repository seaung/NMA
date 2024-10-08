from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    username = models.CharField(max_length=32, unique=True, db_column='username', db_comment='用户名')
    nickname = models.CharField(max_length=32, unique=True, db_column='nickname', db_comment='用户昵称')
    email = models.EmailField(max_length=128, db_column='email', db_comment='电子邮件地址')
    password = models.CharField(max_length=255, db_column='password', db_comment='用户密码')
    dept = models.ForeignKey(to='Departments', on_delete=models.CASCADE, db_constraint=False, null=True, blank=True)
    roles = models.ForeignKey(to='Roles', on_delete=models.CASCADE, db_constraint=False, null=True, blank=True)
    created_at = models.DateTimeField(db_column='created_at', db_comment='用户创建时间', auto_now=True)
    updated_at = models.DateTimeField(db_column='updated_at', db_comment='用户更新时间', auto_now=True)

    def __str__(self):
        return self.username

    def __repr__(self):
        return f'<Users : {self.id} - {self.username}>'

    class Meta:
        db_table = 'nm_users'
        db_table_comment = '用户表'
        ordering = ('-id', )


class Roles(models.Model):
    name = models.CharField(max_length=50, db_column='name', db_comment='角色名称')
    description = models.CharField(max_length=255, db_column='description', db_comment='角色描述')
    enable = models.BooleanField(default=True, db_column='enable', db_comment='是否开启')
    data_scope = models.CharField(max_length=255, db_column='data_scope', db_comment='数据作用范围')
    menus = models.ManyToManyField('Menu', related_name='roles', blank=True)
    departments = models.ManyToManyField('Departments', related_name='roles', blank=True)
    created_at = models.DateTimeField(db_column='created_at', db_comment='角色创建时间', auto_now=True)
    updated_at = models.DateTimeField(db_column='updated_at', db_comment='角色更新时间', auto_now=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self):
        return f'<Roles : {self.id} - {self.name}>'

    class Meta:
        db_table = 'roles'
        db_table_comment = '角色表'


class Departments(models.Model):
    name = models.CharField(max_length=50, db_column='name', db_comment='部门名称')
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    owner = models.CharField(max_length=255, db_column='owner', db_comment='部门主管')
    created_at = models.DateTimeField(db_column='created_at', db_comment='部门创建时间', auto_now=True)
    updated_at = models.DateTimeField(db_column='updated_at', db_comment='部门更新时间', auto_now=True)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Departments {self.id} - {self.name}>'

    class Meta:
        db_table = 'departments'
        db_table_comment = '部门表'
        ordering = ('-id', )


class Permission(models.Model):
    name = models.CharField(max_length=25, unique=True, db_column='name', db_comment='权限名称')
    code = models.CharField(max_length=32, unique=True, db_column='code', db_comment='权限表示码')
    description = models.CharField(max_length=255, db_column='description', db_comment='权限描述')

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Permission : {self.id} - {self.name} - {self.code}>'

    class Meta:
        db_table = 'permission'
        db_table_comment = '权限表'


class Menu(models.Model):
    name = models.CharField(max_length=50, db_column='name', db_comment='菜单名称')
    path = models.CharField(max_length=255, db_column='path', db_comment='跳转路径')
    menu_type = models.CharField(max_length=255, db_column='menu_type', db_comment='菜单类型')
    parent = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True, db_constraint=False, db_comment='上级菜单')
    visible = models.BooleanField(default=True, db_column='visible', db_comment='是否可见')
    created_at = models.DateTimeField(db_column='created_at', db_comment='菜单创建时间')
    updated_at = models.DateTimeField(db_column='updated_at', db_comment='菜单更新时间')

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Menu : {self.id} - {self.path} - {self.menu_type}>'

    class Meta:
        db_table = 'menu'
        db_table_comment = '菜单表'
        ordering = ('-id', )
