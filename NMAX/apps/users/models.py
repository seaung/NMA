from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.db import models


# Create your models here.


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    created_time = models.DateTimeField(auto_now_add=True)


class User(AbstractUser):
    DEFAULT_ROLE_ID = 3
    user_email = models.TextField(blank=True, null=True, default=None, help_text=_('email addresses'))
    phone = models.CharField(max_length=12, blank=True, null=True, default=None, help_text=_('phone number'))
    update_time = models.DateTimeField(auto_now_add=True, verbose_name=_('updated time'))
    password_updated_time = models.DateTimeField(default=now, verbose_name=_('password updated time'))
    role = models.ForeignKey(Role, related_name='users', null=False, on_delete=models.SET_DEFAULT, default=DEFAULT_ROLE_ID)

    def set_password(self, *args, **kwargs):
        self.password_updated_time = now()
        super().set_password(*args, **kwargs)

    @property
    def is_super_user(self) -> bool:
        return self.role.name == 'SUPER_ROLE_USER'

    def is_inactive(self) -> bool:
        return False

    def is_expire(self) -> bool:
        return False

