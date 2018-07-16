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
from time import sleep

from xiaobiaobai.utils import convert_to_uuid, send_bitcash_message, get_transaction_info
from orders.models import OrderModel
import logging

logger = logging.getLogger(__name__)

post_love_word_signal = django.dispatch.Signal(providing_args=['orderid'])
fill_transction_info = django.dispatch.Signal(providing_args=['orderid', 'times'])


@receiver(fill_transction_info)
def fill_order_transction_info(sender, **kwargs):
    orderid = convert_to_uuid(kwargs['orderid'])
    times = int(kwargs['times'])
    try:
        if orderid:
            order = OrderModel.objects.get(id=orderid)
            if order.block_height:
                return
            sleep(times)
            info = get_transaction_info(order.txid)
            if info and info['data']:
                data = info['data']
                block_height = data['block_height']
                order.block_height = block_height
                order.save()
            else:
                fill_order_transction_info.send(sender=fill_order_transction_info.__class__, orderid=orderid,
                                                times=times + 1)
    except Exception as e:
        logger.error(e)


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
        fill_order_transction_info.send(sender=post_love_words.__class__, orderid=orderid,
                                        times=0)
