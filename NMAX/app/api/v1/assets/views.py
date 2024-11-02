from rest_framework import viewsets, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt import authentication


class AssetsManagerViewSets(viewsets.ModelViewSet):
    authentication_classes = (authentication.JWTAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def list(self, request: Request) -> Response:
        return Response()

    def detail(self, request: Request) -> Response:
        return Response()

