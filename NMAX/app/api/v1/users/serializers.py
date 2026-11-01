"""用户/角色/部门/菜单/权限 序列化器"""
from rest_framework import serializers

from app.models.users.users import Departments, Menu, Permission, Roles, Users


class UsersSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(many=True, slug_field="code", queryset=Roles.objects.all(), required=False)
    dept = serializers.PrimaryKeyRelatedField(queryset=Departments.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Users
        fields = (
            "id", "username", "nickname", "email", "phone", "avatar",
            "is_active", "is_superuser", "is_staff", "roles", "dept",
            "last_login_time", "created_at", "updated_at",
        )
        read_only_fields = ("id", "is_superuser", "is_staff", "last_login_time", "created_at", "updated_at")


class CreatedUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Users
        fields = ("id", "username", "nickname", "email", "phone", "avatar", "is_active", "roles", "dept", "password")

    def create(self, validated_data):
        password = validated_data.pop("password")
        roles = validated_data.pop("roles", [])
        user = Users.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=password,
            **{k: v for k, v in validated_data.items() if k not in ("username", "email")},
        )
        if roles:
            user.roles.set(roles)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)


class RolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = "__all__"


class CreatedRolesSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=12, min_length=3)
    code = serializers.CharField(max_length=12, min_length=6)

    class Meta:
        model = Roles
        fields = ("id", "name", "code", "role_type", "description", "enable", "data_scope")


class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = "__all__"


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = "__all__"
