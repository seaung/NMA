from rest_framework import generics, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework import permissions
from rest_framework import status

from .serializers import LoginRequestSerializer, MenuSerializers, PermissionSerializer, DepartmentsSerializer, RolesSerializers


class LoginRequestAPIView(generics.GenericAPIView):
    authentication_classes = (permissions.AllowAny, )
    serializer_class = LoginRequestSerializer

    def post(self, request: Request) -> Response:

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.validated_data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RolesViewSets(viewsets.ModelViewSet):
    ...


class DepartmentsViewSets(viewsets.ModelViewSet):
    ...


class MenuViewSets(viewsets.ModelViewSet):
    ...

