from django.contrib.auth import get_user_model
from rest_framework import generics, views
from rest_framework import permissions
from rest_framework import response
from rest_framework.schemas.coreapi import serializers


from .serializers import ChangeUserPasswordSerializer, UsersSerializer


UserModel = get_user_model()


class CreatedUserGenericsView(generics.CreateAPIView):
    model = UserModel
    permission_classes = [permissions.AllowAny]
    serializer_class = [UsersSerializer]


class ActivateUserAPIView(generics.UpdateAPIView):
    model = UserModel
    permission_classes = [permissions.AllowAny]
    http_method_names = ['patch', 'options']

    def patch(self, request, *args, **kwargs):
        status = self.model.objects.filter(is_active=False, is_staff=False).update(is_active=True, is_staff=True)
        return response.Response(status=status)


class UpdatedUserPasswordAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self, queryset=None):
        return self.request.user

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()

        serializer = ChangeUserPasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.data.get('old_password')
            if not self.object.check_password(old_password):
                return response.Response()

