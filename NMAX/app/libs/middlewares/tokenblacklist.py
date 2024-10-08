from django.utils.deprecation import MiddlewareMixin


class TokenBlackListMiddlewares(MiddlewareMixin):
    def process_request(self, request):
        ...

