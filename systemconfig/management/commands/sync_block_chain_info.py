#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: sync_block_chain_info.py
@time: 2018/6/24 上午2:23
"""

from django.core.management.base import BaseCommand, CommandError
from orders.models import OrderModel
import datetime
from datetime import timedelta
from xiaobiaobai.utils import get_transaction_info


class Command(BaseCommand):
    help = '同步交易'

    def handle(self, *args, **options):
        time = datetime.datetime.now() - timedelta(hours=2)
        orders = OrderModel.objects.filter(order_status='p').filter(txid__isnull=False) \
            .filter(pay_time__gt=time) \
            .all()
        self.stdout.write('开始同步...订单数:{count}'.format(count=len(orders)))
        for o in orders:
            info = get_transaction_info(o.txid)
            if info and info['data']:
                self.stdout.write("开始同步{orderid}.txid:{txid}".format(orderid=o.id, txid=o.txid))
                data = info['data']
                o.block_height = data['block_height']
                o.block_hash = data['block_hash']
                o.save()
            else:
                self.stdout.write("区块获取出错{orderid}.txid:{txid}".format(orderid=o.id, txid=o.txid))
        self.stdout.write('结束同步')
