# Generated by Django 5.0.6 on 2024-10-13 09:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenDisbacklistReacord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField(db_column='user_id', db_comment='用户id')),
                ('username', models.CharField(db_column='username', db_comment='用户名', max_length=32)),
                ('access_token', models.TextField(db_column='access_token', db_comment='access token')),
                ('refresh_token', models.TextField(db_column='refresh_token', db_comment='refresh_token')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_column='created_at', db_comment='created time')),
            ],
            options={
                'db_table': 'token_disbacklist_record',
                'db_table_comment': 'token黑名单表',
                'ordering': ('-id',),
            },
        ),
        migrations.AddField(
            model_name='roles',
            name='departments',
            field=models.ManyToManyField(blank=True, related_name='roles', to='app.departments'),
        ),
        migrations.AddField(
            model_name='roles',
            name='menus',
            field=models.ManyToManyField(blank=True, related_name='roles', to='app.menu'),
        ),
        migrations.AddField(
            model_name='users',
            name='roles',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.roles'),
        ),
        migrations.AlterField(
            model_name='departments',
            name='parent',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='app.departments'),
        ),
    ]