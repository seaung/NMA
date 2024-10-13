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
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def get_serializer_class(self):
        if self.action == 'create':
            return CreatedUserSerializers
        elif self.action == 'update':
            return ChangePasswordSerializer
        return super().get_serializer_class()

    def create(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            password = make_password(request.data.get('password'))
            serializer.save(password=password)
            return Response(status=status.HTTP_201_CREATED, data={})
        return Response(status=status.HTTP_200_OK, data={})

    def update(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            old_password = request.data.get('old_password')
            if check_password(old_password, request.user.password):
                if request.data.get('password') == request.data.get('new_password'):
                    user.set_password(request.data.get('new_password'))
                    user.save()
                    return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)



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
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def create(self, request: Request) -> Response:
        serializer = CreatedRolesSerializers(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_200_OK, data=serializer.validated_data)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={})

    def list(self, request: Request) -> Response:
        roles = Roles.objects.all()
        serializer = RolesSerializers(roles, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class DepartmentsViewSets(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (JWTAuthentication, )

    def create(self, request: Request) -> Response:
        return Response

    def list(self, request, *args, **kwargs) -> Response:
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MenuViewSets(viewsets.ModelViewSet):
    ...

