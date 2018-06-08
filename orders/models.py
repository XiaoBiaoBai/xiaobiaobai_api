import uuid
from django.db import models
from django.utils.timezone import now

# Create your models here.
THIRD_ORDER_CHANNEL = (
    ('w', '微信'),
)


class OrderModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    third_orderid = models.CharField("第三方订单编号", max_length=200, null=True)
    third_orderchannel = models.CharField('第三方订单渠道', max_length=1, choices=THIRD_ORDER_CHANNEL, default='w')

    usermodel = models.ForeignKey('accounts.UserModel', verbose_name='用户', related_name='postusermodel',
                                  on_delete=models.CASCADE, null=True)
    target_usermodel = models.ForeignKey('accounts.UserModel', verbose_name='目标用户', related_name='targetusermodel',
                                         on_delete=models.CASCADE, null=True)
    tx_hex = models.CharField("tx_hex", max_length=2000, null=True)
    txid = models.CharField("txid", max_length=1000, null=True)
    confirmations = models.IntegerField("确认次数", default=0, null=False)
    block_height = models.CharField("块高度", max_length=1000, null=True)
    block_hash = models.CharField("块hash", max_length=2000, null=True)
    fee = models.IntegerField("费用", null=True)

    city = models.CharField('位置', max_length=100, null=True)
    candies_count = models.IntegerField('糖果数目', default=0, null=False)

    order_content = models.CharField("文字", max_length=280, null=True)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return self.__str__()

    class Meta:
        ordering = ['-created_time']
        verbose_name = "订单"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'

        indexes = [
            models.Index(fields=['city', 'third_orderid'])
        ]


class BlessingModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usermodel = models.ForeignKey('accounts.UserModel', verbose_name='祝福用户', on_delete=models.CASCADE)
    ordermodel = models.ForeignKey('orders.OrderModel', verbose_name='订单信息', on_delete=models.CASCADE)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return self.id

    class Meta:
        ordering = ['-created_time']
        verbose_name = "用户祝福信息"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'
