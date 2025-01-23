from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from app.models.token.token import TokenDisbacklistReacord
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import timedelta


class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        try:
            response = super().authenticate(request)
            if response is not None:
                user, validated_token = response
                
                # 获取token字符串
                token_str = validated_token['token'] if 'token' in validated_token else str(validated_token)
                
                # 检查token是否在黑名单中
                if TokenDisbacklistReacord.objects.filter(access_token=token_str).exists():
                    raise InvalidToken(_('token已被禁用'))
                
                # 验证token是否过期
                token = AccessToken(token_str)
                if token.get('exp') < timezone.now().timestamp():
                    raise InvalidToken(_('token已过期'))
                
                # 检查token是否即将过期（比如30分钟内）
                if token.get('exp') - timezone.now().timestamp() < 1800:  # 30分钟 = 1800秒
                    validated_token.set_exp(lifetime=timedelta(hours=2))  # 延长token有效期
                
                return user, validated_token
                
        except TokenError as e:
            raise InvalidToken(_('token验证失败: %s') % str(e))
            
        return None
