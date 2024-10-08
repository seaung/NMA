from rest_framework import generics, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework import permissions
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginRequestSerializer, MenuSerializers, PermissionSerializer, DepartmentsSerializer, RolesSerializers
from app.models.token.token import TokenDisbacklistReacord


class LoginRequestAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = LoginRequestSerializer

    def post(self, request: Request) -> Response:

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.validated_data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutUserGenericAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request: Request) -> Response:
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
    ...


class DepartmentsViewSets(viewsets.ModelViewSet):
    ...


class MenuViewSets(viewsets.ModelViewSet):
    ...

