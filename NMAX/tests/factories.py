"""测试数据工厂：基于 factory_boy，覆盖 RBAC / 资产 / 漏洞 / 工单 核心模型"""
import factory
from django.contrib.auth import get_user_model

from app.models.assets.assets import Asset
from app.models.users.users import Departments, Permission, Roles
from app.models.vulnerabilities.vulnerability import Vulnerability, VulnerabilityAsset
from app.models.workflow.ticket import VulnerabilityTicket

User = get_user_model()


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Departments

    name = factory.Sequence(lambda n: f"部门{n}")
    code = factory.Sequence(lambda n: f"dept-{n}")


class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission

    name = factory.Sequence(lambda n: f"权限{n}")
    code = factory.Sequence(lambda n: f"perm-{n}")


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Roles

    name = factory.Sequence(lambda n: f"角色{n}")
    code = factory.Sequence(lambda n: f"role-{n}")
    data_scope = "SELF"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    nickname = factory.LazyAttribute(lambda o: o.username)
    password = factory.PostGenerationMethodCall("set_password", "Test@123456")


class AssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Asset

    name = factory.Sequence(lambda n: f"资产{n}")
    ip = factory.Sequence(lambda n: f"10.{n // 255}.{(n // 16) % 255}.{n % 255 + 1}")
    asset_type = "host"
    importance = 2
    security_level = "medium"


class VulnerabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vulnerability

    name = factory.Sequence(lambda n: f"漏洞{n}")
    risk_level = "medium"
    status = "unverified"
    source = "manual"
    created_by = factory.SubFactory(UserFactory)


class VulnerabilityAssetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VulnerabilityAsset

    vulnerability = factory.SubFactory(VulnerabilityFactory)
    asset = factory.SubFactory(AssetFactory)


class TicketFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VulnerabilityTicket

    title = factory.Sequence(lambda n: f"工单{n}")
    priority = "medium"
    status = "created"
    creator = factory.SubFactory(UserFactory)
