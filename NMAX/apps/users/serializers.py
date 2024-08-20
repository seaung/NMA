from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


UserModel = get_user_model()


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id', 'username']
        exclude = ['password']


class ChangeUserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return True


class ActivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['is_active', 'is_staff']

