from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.exceptions import InvalidToken
from app.models.token.token import TokenDisbacklistReacord

from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        response = super().authenticate(request)
        if response is not None:
            user, validated_token = response
            token_str = validated_token['token'] if 'token' in validated_token else validated_token
            if TokenDisbacklistReacord.objects.filter(access_token=token_str).exists():
                raise InvalidToken(_('invalid token'))
        return response
