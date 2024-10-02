from rest_framework import views
from rest_framework.request import Request
from rest_framework.response import Response

from rest_framework import permissions
from rest_framework import status

from .serializers import LoginRequestSerializer


class LoginRequestAPIView(views.APIView):
    authentication_classes = (permissions.AllowAny, )

    def post(self, request: Request) -> Response:

        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
