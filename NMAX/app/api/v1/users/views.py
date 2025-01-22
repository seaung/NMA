from django.contrib.auth.hashers import make_password, check_password
from rest_framework import generics, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework import permissions
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
        ChangePasswordSerializer, CreatedUserSerializers, LoginRequestSerializer, MenuSerializers, 
        PermissionSerializer, DepartmentsSerializer, 
        RolesSerializers, CreatedRolesSerializers)
from app.models.token.token import TokenDisbacklistReacord
from app.models.users.users import Roles


class UserManagerViewSets(viewsets.ModelViewSet):
    """用户管理视图集
    
    提供用户的创建、更新等管理功能
    需要JWT认证和登录权限
    """
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get_serializer_class(self):
        """根据不同的操作返回对应的序列化器类
        
        create: 返回用户创建序列化器
        update: 返回密码修改序列化器
        其他: 返回父类默认序列化器
        """
        if self.action == 'create':
            return CreatedUserSerializers
        elif self.action == 'update':
            return ChangePasswordSerializer
        return super().get_serializer_class()

    def create(self, request: Request) -> Response:
        """创建新用户
        
        Args:
            request: 包含用户名和密码的请求
            
        Returns:
            201: 用户创建成功
            200: 验证失败
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = make_password(serializer.validated_data['password'])
            serializer.save(password=password)
            return Response(status=status.HTTP_201_CREATED, data={})
        return Response(status=status.HTTP_200_OK, data={})

    def update(self, request: Request) -> Response:
        """修改用户密码
        
        Args:
            request: 包含旧密码和新密码的请求
            
        Returns:
            200: 密码修改成功
            400: 验证失败
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            old_password = serializer.validated_data['old_password']
            if check_password(old_password, user.password):
                if serializer.validated_data['password'] == serializer.validated_data['new_password']:
                    user.set_password(serializer.validated_data('new_password'))
                    user.save()
                    return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginRequestAPIView(generics.GenericAPIView):
    """用户登录视图
    
    处理用户登录请求，返回JWT token
    不需要认证即可访问
    """
    permission_classes = (permissions.AllowAny, )
    serializer_class = LoginRequestSerializer

    def post(self, request: Request) -> Response:
        """处理登录请求
        
        Args:
            request: 包含用户名和密码的登录请求
            
        Returns:
            200: 登录成功，返回用户信息和token
            400: 登录失败
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.validated_data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserGenericAPIView(generics.GenericAPIView):
    """用户登出视图
    
    处理用户登出请求，将token加入黑名单
    需要登录权限
    """
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request: Request) -> Response:
        """处理登出请求
        
        Args:
            request: 包含access_token和refresh_token的请求
            
        Returns:
            200: 登出成功
            400: 登出失败
        """
        try:
            refresh_token = request.data.get('refresh_token')
            access_token = request.data.get('access_token')
            user_id = request.user.id
            username = request.user.username

            RefreshToken(refresh_token).blacklist()
            TokenDisbacklistReacord.objects.create(
                    user_id=user_id,
                    username=username,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    )
            return Response(status=200, data={'msg': 'success', 'error_code': 100200})
        except Exception:
            return Response(status=400, data={'msg': 'error', 'error_code': 100400})


class RolesViewSets(viewsets.ModelViewSet):
    """角色管理视图集
    
    提供角色的增删改查功能
    需要JWT认证和登录权限
    """
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def create(self, request: Request) -> Response:
        """创建新角色
        
        Args:
            request: 包含角色信息的请求
            
        Returns:
            200: 创建成功
            400: 创建失败
        """
        serializer = CreatedRolesSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.validated_data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={})

    def list(self, request: Request) -> Response:
        """获取所有角色列表
        
        Returns:
            200: 返回角色列表
        """
        roles = Roles.objects.all()
        serializer = RolesSerializers(roles, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """获取单个角色详情"""
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除角色"""
        return super().destroy(request, *args, **kwargs)


class DepartmentsViewSets(viewsets.ModelViewSet):
    """部门管理视图集
    
    提供部门的增删改查功能
    需要JWT认证和登录权限
    """
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def create(self, request: Request) -> Response:
        """创建新部门
        
        Args:
            request: 包含部门信息的请求
            
        Returns:
            201: 创建成功
            400: 创建失败
        """
        serializer = DepartmentsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request: Request) -> Response:
        """获取所有部门列表
        
        Returns:
            200: 返回部门列表
        """
        departments = Departments.objects.all()
        serializer = DepartmentsSerializer(departments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """获取单个部门详情
        
        Returns:
            200: 返回部门详情
        """
        user = self.get_object()
        serializer = CreatedUserSerializers(user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """获取单个部门详情"""
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """删除部门"""
        return super().destroy(request, *args, **kwargs)


class MenuViewSets(viewsets.ModelViewSet):
    """菜单管理视图集
    
    提供菜单的增删改查功能
    需要JWT认证和登录权限
    """
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )
    serializer_class = MenuSerializers

    def create(self, request: Request) -> Response:
        """创建新菜单
        
        Args:
            request: 包含菜单信息的请求
            
        Returns:
            201: 创建成功
            400: 创建失败
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.validated_data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request: Request) -> Response:
        """获取所有菜单列表
        
        Returns:
            200: 返回菜单列表
        """
        menus = Menu.objects.all()
        serializer = self.get_serializer(menus, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """获取单个菜单详情
        
        Returns:
            200: 返回菜单详情
        """
        menu = self.get_object()
        serializer = self.get_serializer(menu)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def update(self, request: Request, *args, **kwargs) -> Response:
        """更新菜单信息
        
        Args:
            request: 包含更新信息的请求
            
        Returns:
            200: 更新成功
            400: 更新失败
        """
        menu = self.get_object()
        serializer = self.get_serializer(menu, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """删除菜单
        
        Returns:
            204: 删除成功
        """
        menu = self.get_object()
        menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

