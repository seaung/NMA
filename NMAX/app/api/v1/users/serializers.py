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


class CreatedUserSerializers(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()


class CreatedRolesSerializers(serializers.ModelSerializer):
    name = serializers.CharField(max_length=12, 
                                 min_length=3, 
                                 required=True,
                                 error_messages={
                                     'required': 'name是必填字段',
                                     'max_length': '最大长度不能超过12',
                                     'min_length': '最小长度不能小于3',
                                     'blank': '字段不能为空',
                                })
    code = serializers.CharField(max_length=12, min_length=6,
                                 required=True, error_messages={
                                     'required': '字段是必填的',
                                     'max_length': '最大长度不能超过12',
                                     'min_length': '最小长度不能小于3',
                                     'blank': '字段不能为空',
                                })


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

        token = RefreshToken.for_user(user)

        return {
                'uuid': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'email': user.email,
                'access_token': str(token.access_token),
                'refresh_token': str(token),
        }

