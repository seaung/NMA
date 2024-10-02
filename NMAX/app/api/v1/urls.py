from django.urls import path

from app.api.v1.users.views import LoginRequestAPIView



urlpatterns = [
    path('user/login', LoginRequestAPIView.as_view(), name='user-login'),
]
