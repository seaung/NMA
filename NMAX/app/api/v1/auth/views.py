"""认证视图：登录 / 刷新 / 登出 / 个人信息 / 修改密码"""
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app.models.users.users import Menu

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    MeSerializer,
    build_menu_tree,
    get_user_permissions,
)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        if ip:
            ip = ip.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        user.last_login_ip = ip
        user.last_login_time = timezone.now()
        user.save(update_fields=["last_login_ip", "last_login_time"])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RefreshView(TokenRefreshView):
    pass


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh")
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except Exception:
                pass
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        data = MeSerializer(user).data
        data["permissions"] = get_user_permissions(user)
        # 汇总角色菜单
        menu_ids = set()
        for role in user.roles.all():
            menu_ids.update(role.menus.values_list("id", flat=True))
        menus_qs = Menu.objects.filter(id__in=menu_ids)
        data["menus"] = build_menu_tree(menus_qs)
        return Response(data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user
        for field in ("nickname", "email", "phone", "avatar"):
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response(MeSerializer(user).data, status=status.HTTP_200_OK)


class PasswordView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"detail": "原密码错误"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.password_changed_at = timezone.now()
        user.save()
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)
