"""认证端点测试：登录 / 个人信息 / 修改密码 / 权限拦截"""
import pytest

from tests.factories import UserFactory


@pytest.mark.django_db
def test_login_success_returns_tokens(api_client):
    u = UserFactory(username="loginuser", email="loginuser@example.com")
    u.set_password("Test@123456")
    u.save()
    resp = api_client.post(
        "/api/v1/auth/login/",
        {"username": "loginuser", "password": "Test@123456"},
        format="json",
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "access" in data and "refresh" in data
    assert data["user"]["username"] == "loginuser"


@pytest.mark.django_db
def test_login_wrong_password_401(api_client):
    u = UserFactory(username="loginuser2", email="loginuser2@example.com")
    u.set_password("Test@123456")
    u.save()
    resp = api_client.post(
        "/api/v1/auth/login/",
        {"username": "loginuser2", "password": "wrong"},
        format="json",
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_returns_permissions_and_menus(api_client, auth_headers, admin_user):
    resp = api_client.get("/api/v1/auth/me/", **auth_headers)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "permissions" in data and "menus" in data
    assert data["username"] == admin_user.username


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/auth/me/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_change_password_success(api_client, auth_headers, admin_user):
    resp = api_client.put(
        "/api/v1/auth/password/",
        {"old_password": "Test@123456", "new_password": "New@123456"},
        format="json",
        **auth_headers,
    )
    assert resp.status_code == 200
    admin_user.refresh_from_db()
    assert admin_user.check_password("New@123456")


@pytest.mark.django_db
def test_change_password_wrong_old(api_client, auth_headers, admin_user):
    resp = api_client.put(
        "/api/v1/auth/password/",
        {"old_password": "wrong", "new_password": "New@123456"},
        format="json",
        **auth_headers,
    )
    assert resp.status_code == 400
