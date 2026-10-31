from django.urls import path, include
from rest_framework.routers import DefaultRouter

from app.api.v1.users.views import (
    LoginRequestAPIView, LogoutUserGenericAPIView,
    UserManagerViewSets, RolesViewSets, DepartmentsViewSets, MenuViewSets,
)
from app.api.v1.assets.views import AssetsManagerViewSets
from app.api.v1.workflow.views import VulnerabilityTicketViewSet

router = DefaultRouter()
router.register(r'users', UserManagerViewSets, basename='users')
router.register(r'roles', RolesViewSets, basename='roles')
router.register(r'departments', DepartmentsViewSets, basename='departments')
router.register(r'menus', MenuViewSets, basename='menus')
router.register(r'assets', AssetsManagerViewSets, basename='assets')
router.register(r'tickets', VulnerabilityTicketViewSet, basename='tickets')

urlpatterns = [
    path('user/login', LoginRequestAPIView.as_view(), name='user-login'),
    path('user/logout', LogoutUserGenericAPIView.as_view(), name='user-logout'),
    path('', include(router.urls)),
]
