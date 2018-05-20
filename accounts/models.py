from django.db import models
from django.utils.timezone import now


# Create your models here.
class UserModel(models.Model):
    username = models.CharField('用户名', max_length=200)
    tel_phone = models.CharField('手机号', max_length=100, null=True)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['-created_time']
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'
