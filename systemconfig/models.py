from django.db import models
from django.utils.timezone import now


# Create your models here.

class SystemConfigMode(models.Model):
    private_key = models.CharField("私钥", max_length=1000, null=False)
    outaddress = models.CharField("转出地址", max_length=1000, null=False, default='')
    leftoveraddress = models.CharField("剩余转入地址", max_length=1000, null=False)
    default_fee = models.IntegerField("默认费用", default=1)
    baidu_appid = models.CharField("百度appid", max_length=1000, null=True)
    baidu_appsecret = models.CharField("百度secret", max_length=1000, null=True)

    weixin_appid = models.CharField("微信appid", max_length=1000, null=False, default='')
    weixin_appsecret = models.CharField("微信app_secret", max_length=1000, null=False, default='')
    mch_id = models.CharField("微信商户id", max_length=1000, null=False, default='')
    mch_key = models.CharField("微信支付密钥", max_length=1000, null=False, default='')
    pay_notify_url = models.CharField("微信支付回调地址", max_length=1000, null=False, default='')
    wx_sign_type = models.CharField("微信签名类型", default='md5', null=False, max_length=1000)
    wx_remote_addr = models.CharField("服务器IP地址", default='', null=False, max_length=1000)
    wx_scope = models.CharField("微信授权类型", default='snsapi_base', null=False, max_length=1000)
    wx_redirect_uri = models.CharField("微信登录重定向地址", null=False, default='', max_length=1000)
    wx_token = models.CharField("微信公众号授权token", default='', max_length=1000)

    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return self.leftoveraddress

    def __repr__(self):
        result = ','.join(['%s::%s' % (k, v) for k, v in self.__dict__.items() if not k.startswith('_')])
        return result

    class Meta:
        ordering = ['-created_time']
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'
