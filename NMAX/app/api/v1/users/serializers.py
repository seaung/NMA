from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from app.models.users.users import Permission, Menu, Roles, Departments


Users = get_user_model()


class RolesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'


class DepartmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departments
        fields = '__all__'


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class MenuSerializers(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'


class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        user = Users.objects.filter(username=username).first()
        if not user:
            raise ValidationError('用户名或密码错误')
        if not user.check_password(password):
            raise ValidationError('用户名或密码错误')

        #token = TokenObtainSerializer.get_token(user)
        token = RefreshToken.for_user(user)

        return {
                'uuid': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'email': user.email,
                'access_token': str(token.access_token),
                'refresh_token': str(token),
        }

    #class Meta:
    #    model = Users
    #    fields = ('id', 'username', 'nickname', 'email')

