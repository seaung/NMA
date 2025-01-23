from django.db import models
from django.utils import timezone


class Assets(models.Model):
    """资产模型
    
    用于存储和管理资产信息
    """
    STATUS_CHOICES = (
        ('in_use', '使用中'),
        ('idle', '闲置'),
        ('maintenance', '维护中'),
        ('scrapped', '已报废'),
    )

    TYPE_CHOICES = (
        ('hardware', '硬件设备'),
        ('software', '软件'),
        ('network', '网络设备'),
        ('other', '其他'),
    )

    name = models.CharField('资产名称', max_length=100)
    asset_type = models.CharField('资产类型', max_length=20, choices=TYPE_CHOICES)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='idle')
    serial_number = models.CharField('序列号', max_length=100, unique=True)
    purchase_date = models.DateField('购买日期')
    price = models.DecimalField('价格', max_digits=10, decimal_places=2)
    description = models.TextField('描述', blank=True)
    location = models.CharField('位置', max_length=100)
    manufacturer = models.CharField('制造商', max_length=100)
    model = models.CharField('型号', max_length=100)
    owner = models.ForeignKey('users.Users', on_delete=models.SET_NULL, null=True, verbose_name='负责人')
    department = models.ForeignKey('users.Departments', on_delete=models.SET_NULL, null=True, verbose_name='所属部门')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '资产'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name