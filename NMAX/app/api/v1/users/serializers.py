from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from django.contrib.auth import get_user_model


Users = get_user_model()


class LoginRequestSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs['username']
        password = attrs['password']

        user = Users.objects.filter(username=username)
        if not user:
            raise ValidationError('')
        if not user.check_password(password):
            raise ValidationError('')

        token = TokenObtainSerializer(user)

        return {
                'uuid': user.id,
                'username': user.username,
                'nickname': user.nickname,
                'email': user.email,
                'access_token': token
        }

    class Meta:
        model = Users
        fields = ('id', 'username', 'nickname', 'email')

