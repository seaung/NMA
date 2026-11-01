"""测试夹具：API 客户端、管理员、带权限的普通用户、JWT 请求头"""
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from app.models.users.users import Permission, Roles
from tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return UserFactory(is_superuser=True, is_staff=True)


@pytest.fixture
def auth_headers(admin_user):
    token = RefreshToken.for_user(admin_user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token.access_token}"}


@pytest.fixture
def report_role(db):
    role = Roles.objects.create(name="报表员", code="reporter", data_scope="ALL")
    perm = Permission.objects.create(name="报表查看", code="report:view", type="OPERATION")
    role.permissions.add(perm)
    return role


@pytest.fixture
def reporter_user(db, report_role):
    user = UserFactory()
    user.roles.add(report_role)
    return user


def make_auth_headers(user):
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token.access_token}"}
