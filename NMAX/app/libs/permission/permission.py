from django.core.cache import cache
from django.conf import settings
from rest_framework.permissions import BasePermission
from typing import List, Optional


class HasPermission(BasePermission):
    def get_user_permissions(self, user) -> List[str]:
        """获取用户所有权限，包括直接权限和角色权限
        
        Args:
            user: 用户对象
            
        Returns:
            权限名称列表
        """
        cache_key = f'user_permissions_{user.id}'
        cached_permissions = cache.get(cache_key)
        
        if cached_permissions is not None:
            return cached_permissions
            
        # 获取用户直接权限
        direct_permissions = set(user.permissions.values_list('name', flat=True))
        
        # 获取角色权限
        role_permissions = set()
        for role in user.roles.all():
            role_permissions.update(role.permissions.values_list('name', flat=True))
            
        # 合并所有权限
        all_permissions = list(direct_permissions | role_permissions)
        
        # 缓存权限列表
        cache_timeout = getattr(settings, 'PERMISSION_CACHE_TIMEOUT', 300)  # 默认5分钟
        cache.set(cache_key, all_permissions, cache_timeout)
        
        return all_permissions
    
    def check_api_permission(self, request, view) -> bool:
        """检查API权限
        
        Args:
            request: 请求对象
            view: 视图对象
            
        Returns:
            是否有权限
        """
        required_permissions = getattr(view, 'required_permissions', [])
        if not required_permissions:
            return True
            
        user_permissions = self.get_user_permissions(request.user)
        return all(perm in user_permissions for perm in required_permissions)
    
    def check_data_permission(self, request, view) -> bool:
        """检查数据权限
        
        Args:
            request: 请求对象
            view: 视图对象
            
        Returns:
            是否有权限
        """
        # 获取数据权限过滤器
        data_filter = getattr(view, 'data_permission_filter', None)
        if data_filter is None:
            return True
            
        return data_filter(request.user)
    
    def has_permission(self, request, view) -> bool:
        """权限检查入口
        
        Args:
            request: 请求对象
            view: 视图对象
            
        Returns:
            是否有权限
        """
        user = request.user
        
        # 检查是否登录
        if not user.is_authenticated:
            return False
            
        # 超级管理员拥有所有权限
        if user.is_superuser:
            return True
            
        # 检查API权限
        if not self.check_api_permission(request, view):
            return False
            
        # 检查数据权限
        return self.check_data_permission(request, view)


