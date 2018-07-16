import uuid
from django.db import models
from django.utils.timezone import now
from django.utils.functional import cached_property
from django.core.cache import cache
from xiaobiaobai.utils import get_transaction_info, cache_decorator, get_latest_block

import logging

logger = logging.getLogger(__name__)

# Create your models here.
THIRD_ORDER_CHANNEL = (
    ('w', '微信'),
)
ORDER_STATUS = (

    ('c', '创建'),
    ('p', '已支付'),
)


class OrderModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    third_orderid = models.CharField("第三方订单编号", max_length=200, null=True)
    third_orderchannel = models.CharField('第三方订单渠道', max_length=1, choices=THIRD_ORDER_CHANNEL, default='w')
    order_status = models.CharField("订单状态", max_length=1, choices=ORDER_STATUS, null=False, default='c')
    pay_time = models.DateTimeField("付款时间", null=True)
    usermodel = models.ForeignKey('accounts.UserModel', verbose_name='用户', related_name='postusermodel',
                                  on_delete=models.CASCADE, null=True)
    username = models.CharField("发布对象用户名", null=True, max_length=300)
    target_username = models.CharField("发布对象用户名", null=True, max_length=300)
    show_confession_wall = models.BooleanField('是否在表白墙显示', null=False, default=True)

    tx_hex = models.CharField("tx_hex", max_length=2000, null=True)
    txid = models.CharField("txid", max_length=1000, null=True)
    block_height = models.IntegerField("打包的时候块高度", null=True)
    block_hash = models.CharField("块hash", max_length=2000, null=True)
    fee = models.IntegerField("费用", null=True)

    background_img = models.CharField("背景图片地址", null=False, default='', max_length=1000)

    city = models.CharField('位置', max_length=100, null=True)
    candies_count = models.IntegerField('糖果数目', default=0, null=False)
    wx_prepayid = models.CharField("微信prepayid", max_length=300, null=True)
    order_content = models.CharField("文字", max_length=280, null=True)
    created_time = models.DateTimeField('创建时间', default=now)
    last_mod_time = models.DateTimeField('修改时间', default=now)

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return self.__str__()

    @property
    def block_chain_url(self):
        if self.txid:
            return 'https://explorer.bitcoin.com/bch/tx/' + self.txid
        return ''

    @property
    def can_send_blessing(self):
        if hasattr(self, 'queryuserid'):
            from xiaobiaobai.utils import convert_to_uuid
            userid = convert_to_uuid(getattr(self, 'queryuserid'))
            count = self.blessingmodel_set.filter(usermodel=userid).count()
            return count <= 0
        return True

    @property
    def confirmations(self):
        if self.txid and self.block_height:
            try:
                latestblock = get_latest_block()
                if latestblock and latestblock != 0:
                    count = int(latestblock) - self.block_height + 1
                    return count
            except Exception as e:
                logger.error(e)
                return 0
        return 0

    @property
    @cache_decorator(1 * 60)
    def blessing_count(self):
        return self.blessingmodel_set.count()

    class Meta:
        ordering = ['-created_time']
        verbose_name = "订单"
        verbose_name_plural = verbose_name
        get_latest_by = 'created_time'

        indexes = [
            models.Index(fields=['city', 'third_orderid'])
        ]


class WxOrderModel(models.Model):
    pass


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
