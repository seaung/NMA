from django.db import models
from django.contrib.auth.models import AbstractUser


class Users(AbstractUser):
    username = models.CharField(max_length=32, unique=True, db_column='username', db_comment='用户名')
    nickname = models.CharField(max_length=32, unique=True, db_column='nickname', db_comment='用户昵称')
    email = models.EmailField(max_length=128, db_column='email', db_comment='电子邮件地址')
    password = models.CharField(max_length=255, db_column='password', db_comment='用户密码')

    def __str__(self):
        return self.username

    def __repr__(self):
        return f'<Users : {self.id} - {self.username}>'

    class Meta:
        db_table = 'nm_users'
        db_table_comment = '用户表'
        ordering = ('-id', )
