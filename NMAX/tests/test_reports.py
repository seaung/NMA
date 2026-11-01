"""合規報表匯出接口测试：鉴权、权限、合法 Excel 产物"""
import pytest
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import UserFactory


def _headers(user):
    token = RefreshToken.for_user(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token.access_token}"}


@pytest.mark.django_db
def test_reports_requires_auth(api_client):
    assert api_client.get("/api/v1/reports/").status_code == 401


@pytest.mark.django_db
def test_reports_admin_export_xlsx(api_client, auth_headers):
    resp = api_client.get("/api/v1/reports/", **auth_headers)
    assert resp.status_code == 200
    assert "spreadsheetml" in resp["Content-Type"]
    assert len(resp.content) > 0


@pytest.mark.django_db
def test_reports_forbidden_without_permission(api_client):
    user = UserFactory()  # 无 report:view 权限
    resp = api_client.get("/api/v1/reports/", **_headers(user))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_reports_allowed_with_permission(api_client, reporter_user):
    resp = api_client.get("/api/v1/reports/", **_headers(reporter_user))
    assert resp.status_code == 200
    assert "spreadsheetml" in resp["Content-Type"]


@pytest.mark.django_db
def test_reports_vulnerabilities_type(api_client, auth_headers):
    resp = api_client.get("/api/v1/reports/?type=vulnerabilities", **auth_headers)
    assert resp.status_code == 200
    assert "spreadsheetml" in resp["Content-Type"]
