from django.db import models

# Create your models here.


class Configs(models.Model):
    conf_type = models.CharField('conf_type', max_length=12, db_comment='配置类型')
    conf_value = models.CharField('conf_value', max_length=255, db_comment='配置值')
    conf_enable = models.BooleanField('conf_enable', default=False, db_comment='是否开启配置')


    class Meta:
        db_table = 'nm_configs'
