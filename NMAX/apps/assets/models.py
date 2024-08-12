from django.db import models
from django.utils.translation import gettext_lazy as _


class HostAssetsModel(models.Model):
    ipaddr = models.CharField(max_length=50, verbose_name=_('addresses'))
    source = models.CharField(max_length=30, verbose_name=_('source'))
    location = models.CharField(max_length=30, verbose_name=_('location'))
    manager = models.CharField(max_length=30, verbose_name=_('manager'))

    class Meta:
        managed = False
        db_table = 'host_assets_model'


class PortAssetsModel(models.Model):
    ipaddr = models.CharField(max_length=50, verbose_name=_('addresses'))
    source = models.CharField(max_length=30, verbose_name=_('source'))
    location = models.CharField(max_length=30, verbose_name=_('location'))
    ports = models.CharField(max_length=255, verbose_name=_('ports'))
    state = models.CharField(max_length=20, verbose_name=_('state'))
    manager = models.CharField(max_length=30, verbose_name=_('manager'))

    class Meta:
        managed = False
        db_table = 'port_assets_model'

