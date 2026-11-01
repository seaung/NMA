from django.urls import include, path
from rest_framework.routers import DefaultRouter

from app.api.v1.assets.views import AssetsManagerViewSets
from app.api.v1.auth.views import (
    LoginView,
    LogoutView,
    MeView,
    PasswordView,
    RefreshView,
)
from app.api.v1.dashboard.views import DashboardView
from app.api.v1.messages.views import MessageViewSet
from app.api.v1.reports.views import ReportsView
from app.api.v1.tasks.views import TaskViewSet
from app.api.v1.users.views import (
    DepartmentsViewSets,
    MenuViewSets,
    PermissionViewSets,
    RolesViewSets,
    UserManagerViewSets,
)
from app.api.v1.vulnerabilities.views import VulnerabilityViewSet
from app.api.v1.workflow.views import VulnerabilityTicketViewSet

router = DefaultRouter()
router.register(r"users", UserManagerViewSets, basename="users")
router.register(r"roles", RolesViewSets, basename="roles")
router.register(r"departments", DepartmentsViewSets, basename="departments")
router.register(r"menus", MenuViewSets, basename="menus")
router.register(r"permissions", PermissionViewSets, basename="permissions")
router.register(r"assets", AssetsManagerViewSets, basename="assets")
router.register(r"vulnerabilities", VulnerabilityViewSet, basename="vulnerabilities")
router.register(r"tickets", VulnerabilityTicketViewSet, basename="tickets")
router.register(r"messages", MessageViewSet, basename="messages")
router.register(r"tasks", TaskViewSet, basename="tasks")

urlpatterns = [
    # 认证
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", RefreshView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("auth/password/", PasswordView.as_view(), name="auth-password"),
    # 仪表盘与报表
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("reports/", ReportsView.as_view(), name="reports"),
    # 资源路由
    path("", include(router.urls)),
]
