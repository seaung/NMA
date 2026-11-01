"""数据范围（行级权限）测试"""
import pytest

from app.libs.permission.data_scope import filter_by_data_scope, get_data_scope
from app.models.assets.assets import Asset
from app.models.users.users import Roles
from tests.factories import AssetFactory, DepartmentFactory, UserFactory


@pytest.mark.django_db
def test_superuser_sees_all():
    user = UserFactory(is_superuser=True, is_staff=True)
    assert get_data_scope(user) == (True, set())


@pytest.mark.django_db
def test_self_scope_filters_by_owner():
    user = UserFactory()
    other = UserFactory()
    role = Roles.objects.create(name="自管", code="self-role", data_scope="SELF")
    user.roles.add(role)
    AssetFactory(created_by=user)
    AssetFactory(created_by=other)
    qs = filter_by_data_scope(
        Asset.objects.all(), user, dept_field="department", owner_field="created_by"
    )
    assert qs.count() == 1
    assert qs.first().created_by_id == user.id


@pytest.mark.django_db
def test_dept_scope_filters_by_department():
    dept = DepartmentFactory()
    other = DepartmentFactory()
    user = UserFactory(dept=dept)
    role = Roles.objects.create(name="本部门", code="dept-role", data_scope="DEPT")
    user.roles.add(role)
    AssetFactory(department=dept, created_by=user)
    AssetFactory(department=other, created_by=user)
    qs = filter_by_data_scope(Asset.objects.all(), user, dept_field="department")
    assert qs.count() == 1


@pytest.mark.django_db
def test_all_scope_returns_full_queryset():
    user = UserFactory()
    role = Roles.objects.create(name="全部", code="all-role", data_scope="ALL")
    user.roles.add(role)
    AssetFactory()
    AssetFactory()
    assert filter_by_data_scope(Asset.objects.all(), user).count() == 2
