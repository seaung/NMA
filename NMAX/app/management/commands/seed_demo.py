"""初始化演示数据：管理员、部门、角色、菜单、资产、漏洞、工单、消息、系统配置"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models.assets.assets import Asset
from app.models.system.message import Message, MessageRecipient
from app.models.system.system_config import SystemConfig
from app.models.users.users import Departments, Menu, Permission, Roles, Users
from app.models.vulnerabilities.vulnerability import Vulnerability
from app.models.workflow.ticket import VulnerabilityTicket


class Command(BaseCommand):
    help = "初始化 NMA 演示数据"

    def handle(self, *args, **options):
        self.stdout.write("开始初始化演示数据...")

        # 系统配置默认值
        self.seed_config()

        # 部门
        dept, _ = Departments.objects.get_or_create(
            code="sec", defaults={"name": "安全运营部", "sort": 1}
        )

        # 角色
        admin_role, _ = Roles.objects.get_or_create(
            code="admin", defaults={"name": "管理员", "role_type": "SYSTEM",
                                    "data_scope": "ALL", "enable": True}
        )
        security_role, _ = Roles.objects.get_or_create(
            code="security", defaults={"name": "安全工程师", "role_type": "CUSTOM",
                                       "data_scope": "DEPT_AND_CHILD", "enable": True}
        )

        # 权限（用于 RBAC）
        self.seed_permissions(admin_role, security_role)

        # 菜单
        self.seed_menus(admin_role, security_role)

        # 管理员
        admin, created = Users.objects.get_or_create(
            username="admin", defaults={"email": "admin@nma.local", "nickname": "管理员"}
        )
        if created:
            admin.set_password("admin1234")
            admin.is_superuser = True
            admin.is_staff = True
            admin.dept = dept
            admin.save()
            admin.roles.add(admin_role)
        self.stdout.write(self.style.SUCCESS("管理员账号: admin / admin1234"))

        # 普通安全工程师
        sec_user, created = Users.objects.get_or_create(
            username="secuser", defaults={"email": "sec@nma.local", "nickname": "安全工程师"}
        )
        if created:
            sec_user.set_password("sec1234")
            sec_user.dept = dept
            sec_user.save()
            sec_user.roles.add(security_role)
        self.stdout.write(self.style.SUCCESS("安全工程师账号: secuser / sec1234"))

        # 资产
        assets = self.seed_assets(dept, sec_user)

        # 漏洞
        vulnerabilities = self.seed_vulnerabilities(assets, sec_user)

        # 工单
        self.seed_tickets(vulnerabilities, assets, sec_user, dept)

        # 消息
        self.seed_messages(admin, sec_user)

        self.stdout.write(self.style.SUCCESS("演示数据初始化完成。"))

    def seed_config(self):
        defaults = [
            ("login_max_attempts", 5, "最大登录失败次数"),
            ("account_lockout_minutes", 30, "账户锁定时长(分钟)"),
            ("sla_critical_hours", 24, "严重漏洞SLA(小时)"),
            ("sla_high_hours", 72, "高危漏洞SLA(小时)"),
            ("sla_medium_hours", 168, "中危漏洞SLA(小时)"),
            ("sla_low_hours", 720, "低危漏洞SLA(小时)"),
        ]
        for key, value, desc in defaults:
            SystemConfig.set_value(key, value, description=desc, is_system=True)

    def seed_permissions(self, admin_role, security_role):
        perms = [
            ("asset:view", "资产查看", "OPERATION"),
            ("asset:manage", "资产管理", "OPERATION"),
            ("vuln:view", "漏洞查看", "OPERATION"),
            ("vuln:manage", "漏洞管理", "OPERATION"),
            ("ticket:view", "工单查看", "OPERATION"),
            ("ticket:manage", "工单管理", "OPERATION"),
            ("task:view", "任务查看", "OPERATION"),
            ("task:manage", "任务管理", "OPERATION"),
            ("report:view", "报表查看", "OPERATION"),
            ("report:export", "报表导出", "OPERATION"),
            ("user:view", "用户查看", "OPERATION"),
            ("user:manage", "用户管理", "OPERATION"),
            ("role:manage", "角色管理", "OPERATION"),
            ("dept:manage", "部门管理", "OPERATION"),
            ("menu:manage", "菜单管理", "OPERATION"),
            ("perm:manage", "权限管理", "OPERATION"),
            ("system:view", "系统查看", "OPERATION"),
        ]
        created = []
        for code, name, ptype in perms:
            p, _ = Permission.objects.get_or_create(
                code=code, defaults={"name": name, "type": ptype}
            )
            created.append(p)
        admin_role.permissions.set(created)
        security_codes = {"asset:view", "asset:manage", "vuln:view", "vuln:manage",
                          "ticket:view", "ticket:manage", "task:view", "task:manage",
                          "report:view", "report:export"}
        security_role.permissions.set([p for p in created if p.code in security_codes])
        return created

    def seed_menus(self, admin_role, security_role):
        menus = [
            ("仪表盘", "/dashboard", "dashboard", "Layout", 1),
            ("资产管理", "/assets", "assets", "ClusterOutlined", 2),
            ("漏洞管理", "/vulnerabilities", "vulnerabilities", "BugOutlined", 3),
            ("工单管理", "/tickets", "tickets", "SolutionOutlined", 4),
            ("任务管理", "/tasks", "tasks", "RadarChartOutlined", 5),
            ("消息中心", "/messages", "messages", "BellOutlined", 6),
            ("合规报表", "/reports", "reports", "FileTextOutlined", 7),
            ("系统管理", "/system", "system", "SettingOutlined", 8),
        ]
        created = []
        for name, path, code, icon, sort in menus:
            m, _ = Menu.objects.get_or_create(
                path=path, defaults={"name": name, "component": code,
                                     "icon": icon, "sort": sort, "menu_type": "menu"}
            )
            created.append(m)
        admin_role.menus.add(*created)
        security_role.menus.add(*created)

    def seed_assets(self, dept, user):
        data = [
            ("Web 门户服务器", "10.0.0.11", "web-portal", "host", "high"),
            ("核心数据库", "10.0.0.21", "db-core", "database", "critical"),
            ("边界防火墙", "203.0.113.1", "edge-fw", "network", "medium"),
            ("OA 应用服务器", "10.0.0.31", "oa-app", "web", "high"),
        ]
        assets = []
        for name, ip, hostname, atype, level in data:
            a, _ = Asset.objects.get_or_create(
                ip=ip, defaults={
                    "name": name, "hostname": hostname, "asset_type": atype,
                    "security_level": level, "department": dept, "manager": user,
                    "asset_status": "in_use", "importance": 3 if level in ("critical", "high") else 2,
                    "exposed": atype in ("network", "web"),
                    "created_by": user,
                }
            )
            assets.append(a)
        return assets

    def seed_vulnerabilities(self, assets, user):
        data = [
            ("Apache Log4j 远程代码执行", "CVE-2021-44228", "critical", "scan", "unverified"),
            ("OpenSSL 心脏滴血", "CVE-2014-0160", "high", "manual", "verified"),
            ("Redis 未授权访问", None, "medium", "scan", "fixing"),
            ("Nginx 版本过低", None, "low", "scan", "pending_retest"),
        ]
        vulns = []
        for i, (name, cve, level, source, status) in enumerate(data):
            v, _ = Vulnerability.objects.get_or_create(
                name=name, cve_id=cve, defaults={
                    "risk_level": level, "source": source, "status": status,
                    "description": f"{name} 演示漏洞数据", "impact": "可能导致远程代码执行或信息泄露",
                    "solution": "升级到安全版本并配置访问控制", "cvss_score": 9.0 if level == "critical" else 7.0,
                    "created_by": user,
                }
            )
            # 关联一个资产
            if assets:
                v.assets.get_or_create(asset=assets[i % len(assets)], defaults={"port": "443", "protocol": "https"})
            vulns.append(v)
        return vulns

    def seed_tickets(self, vulns, assets, user, dept):
        if not vulns:
            return
        t, _ = VulnerabilityTicket.objects.get_or_create(
            title="处理 Log4j 漏洞", defaults={
                "priority": "critical", "status": "processing",
                "description": "紧急处理核心系统 Log4j 漏洞", "creator": user,
                "assignee": user, "department": dept, "deadline": timezone.now() + timezone.timedelta(days=1),
            }
        )
        if vulns:
            t.vulnerability = vulns[0]
            if assets:
                t.asset = assets[0]
            t.save()

    def seed_messages(self, admin, user):
        msg, _ = Message.objects.get_or_create(
            title="欢迎使用 NMA 漏洞运营系统",
            defaults={"content": "系统已完成初始化，可开始录入资产与漏洞。", "message_type": "system",
                      "level": "info", "sender": admin},
        )
        MessageRecipient.objects.get_or_create(message=msg, recipient=user)
