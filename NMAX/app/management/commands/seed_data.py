"""初始化系统种子数据。

用法:
    python manage.py seed_data
    python manage.py seed_data --admin-password YourPassword

幂等：可重复执行，已存在的记录不会重复创建。
"""
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand

from app.models.users.users import Departments, Roles, Users


class Command(BaseCommand):
    help = '创建默认管理员、部门与角色等种子数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-password',
            default='Admin@123456',
            help='超级管理员初始密码（默认 Admin@123456）',
        )

    def handle(self, *args, **options):
        # 1. 默认部门
        hq, created = Departments.objects.get_or_create(
            name='安全运营部',
            defaults={'owner': 'admin'},
        )
        dev, _ = Departments.objects.get_or_create(
            name='研发部',
            defaults={'owner': 'admin'},
        )
        self._report(Departments, [(hq.name, created), (dev.name, None)])

        # 2. 默认角色
        roles = []
        for name, code, role_type, scope, desc in [
            ('系统管理员', 'ADMIN', 'SYSTEM', 'ALL', '拥有全部数据与功能权限'),
            ('安全审计员', 'AUDITOR', 'CUSTOM', 'DEPT', '查看与处置本部门漏洞'),
            ('开发负责人', 'DEV_LEAD', 'CUSTOM', 'DEPT', '承接漏洞修复工单'),
        ]:
            role, created = Roles.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'role_type': role_type,
                    'data_scope': scope,
                    'description': desc,
                },
            )
            roles.append(role)
            self._report(Roles, [(name, created)])

        # 3. 超级管理员
        admin, created = Users.objects.get_or_create(
            username='admin',
            defaults={
                'nickname': '系统管理员',
                'email': 'admin@nma.local',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
                'dept': hq,
            },
        )
        if created:
            admin.password = make_password(options['admin_password'])
            admin.save()
        admin.roles.add(*roles)
        self._report(Users, [(admin.username, created)])

        self.stdout.write(self.style.SUCCESS('[OK] 种子数据初始化完成'))

    @staticmethod
    def _report(model, items):
        for name, created in items:
            status = '创建' if created else ('已存在' if created is not None else '就绪')
            print(f'  {model.__name__}: {name} ({status})')
