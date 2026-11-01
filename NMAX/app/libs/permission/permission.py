from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):
    """基于权限码(permission.code)的访问控制，并支持数据范围"""

    def get_user_permissions(self, user) -> list:
        cache_key = f"user_permissions_{user.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # 直接权限
        direct = set(user.permissions.values_list("code", flat=True))
        # 角色权限
        role_perms = set()
        for role in user.roles.all():
            role_perms.update(role.permissions.values_list("code", flat=True))

        all_perms = list(direct | role_perms)
        timeout = getattr(settings, "PERMISSION_CACHE_TIMEOUT", 300)
        cache.set(cache_key, all_perms, timeout)
        return all_perms

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user.is_authenticated:
            return False
        # 超级管理员拥有全部权限
        if user.is_superuser:
            return True

        # API 权限：视图声明 required_permissions（权限码列表）
        required = getattr(view, "required_permissions", [])
        if required:
            user_perms = self.get_user_permissions(user)
            if not all(perm in user_perms for perm in required):
                return False
        return True
