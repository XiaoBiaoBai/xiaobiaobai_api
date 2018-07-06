#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: signals.py
@time: 2018/6/24 上午1:13
"""

import django.dispatch
from django.dispatch import receiver
from django.conf import settings

from xiaobiaobai.utils import convert_to_uuid, send_bitcash_message
from orders.models import OrderModel
import logging

logger = logging.getLogger(__name__)

post_love_word_signal = django.dispatch.Signal(providing_args=['orderid'])


@receiver(post_love_word_signal)
def post_love_words(sender, **kwargs):
    orderid = convert_to_uuid(kwargs['orderid'])
    logger.info('开始发送' + str(orderid))
    if orderid:
        order = OrderModel.objects.get(id=orderid)
        if order.txid and order.tx_hex:
            logger.info('{orderid}已经成功广播'.format(orderid=orderid))
            return
        txhash, txid = send_bitcash_message(order.order_content)
        logger.info('txhash:{txhash},txid:{txid}'.format(txhash=txhash, txid=txid))
        order.txid = txid
        order.tx_hex = txhash
        order.save()
