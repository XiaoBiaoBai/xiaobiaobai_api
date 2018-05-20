from django.db import models
from django.utils.timezone import now


# Create your models here.

class SystemConfigMode(models.Model):
    private_key = models.CharField("私钥", max_length=1000, null=False)
    leftoveraddress = models.CharField("转入地址", max_length=1000, null=False)
    default_fee = models.IntegerField("默认费用", default=1)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return self.leftoveraddress

    class Meta:
        ordering = ['-created_time']
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'
