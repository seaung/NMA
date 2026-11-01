"""用户/角色/部门/菜单 视图"""
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from app.libs.permission.permission import HasPermission
from app.models.users.users import Departments, Menu, Permission, Roles, Users

from .serializers import (
    CreatedUserSerializer,
    DepartmentsSerializer,
    MenuSerializer,
    PermissionSerializer,
    RolesSerializer,
    UsersSerializer,
)


class UserManagerViewSets(viewsets.ModelViewSet):
    queryset = Users.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (HasPermission,)
    required_permissions = ["user:view"]

    def get_serializer_class(self):
        if self.action == "create":
            return CreatedUserSerializer
        return UsersSerializer

    def create(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UsersSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)


class RolesViewSets(viewsets.ModelViewSet):
    queryset = Roles.objects.all()
    serializer_class = RolesSerializer
    permission_classes = (HasPermission,)
    required_permissions = ["role:manage"]


class DepartmentsViewSets(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentsSerializer
    permission_classes = (HasPermission,)
    required_permissions = ["dept:manage"]


class MenuViewSets(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = (HasPermission,)
    required_permissions = ["menu:manage"]


class PermissionViewSets(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = (HasPermission,)
    required_permissions = ["perm:manage"]
