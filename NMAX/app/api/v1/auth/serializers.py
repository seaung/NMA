"""认证相关序列化器"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.models.users.users import Users


class LoginSerializer(TokenObtainPairSerializer):
    """登录：在 token 基础上附加用户信息"""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "roles": list(user.roles.values_list("code", flat=True)),
        }
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=8)


def build_menu_tree(menus):
    """将菜单列表构建为树形结构"""
    menu_list = list(menus.values("id", "name", "path", "component", "icon", "menu_type", "parent_id", "visible", "permission_id"))
    by_parent = {}
    for m in menu_list:
        by_parent.setdefault(m["parent_id"], []).append(m)
    tree = []

    def to_node(m):
        node = {
            "id": m["id"],
            "name": m["name"],
            "path": m["path"],
            "component": m["component"],
            "icon": m["icon"],
            "menu_type": m["menu_type"],
            "visible": m["visible"],
            "permission_id": m["permission_id"],
            "children": [],
        }
        for child in by_parent.get(m["id"], []):
            node["children"].append(to_node(child))
        return node

    for m in by_parent.get(None, []):
        tree.append(to_node(m))
    return tree


class MeSerializer(serializers.ModelSerializer):
    roles = serializers.SlugRelatedField(many=True, slug_field="code", read_only=True)
    dept = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = (
            "id", "username", "nickname", "email", "phone", "avatar",
            "is_active", "is_superuser", "is_staff", "roles", "dept",
            "last_login_time", "created_at", "updated_at",
        )
        read_only_fields = fields

    def get_dept(self, obj):
        return {"id": obj.dept.id, "name": obj.dept.name} if obj.dept else None


def get_user_permissions(user):
    if user.is_superuser:
        return ["*"]
    direct = set(user.permissions.values_list("code", flat=True))
    role_perms = set()
    for role in user.roles.all():
        role_perms.update(role.permissions.values_list("code", flat=True))
    return list(direct | role_perms)
