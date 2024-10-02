from django.db import models
from django.contrib.auth import get_user_model


Users = get_user_model()


class TokenDisbacklistReacord(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    access_token = models.TextField(db_column='access_token', db_comment='access token')
    refresh_token = models.TextField(db_column='refresh_token', db_comment='refresh_token')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at', db_comment='created time')
    expires_at = models.DateTimeField(db_column='expires_at', db_comment='expires time')

    def __str__(self) -> str:
        return self.access_token

    def __repr__(self) -> str:
        return f'<TokenDisbacklistReacord {self.id} - {self.access_token}>'

    class Meta:
        db_table = 'token_disbacklist_record'
        db_table_comment = 'token黑名单表'
        ordering = ('-id', )

