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

from xiaobiaobai.utils import get_transaction_info


class Command(BaseCommand):
    help = '同步交易'

    def handle(self, *args, **options):

        self.stdout.write('开始同步...')
        orders = OrderModel.objects.filter(order_status='p').filter(txid__isnull=False) \
            .filter(block_height__isnull=True) \
            .all()

        for o in orders:
            info = get_transaction_info(o.txid)
            if info and info['data']:
                self.stdout.write("开始同步{orderid}.txid:{txid}".format(orderid=o.id, txid=o.txid))
                data = info['data']
                o.block_height = data['block_height']
                o.block_hash = data['block_hash']
                o.save()
        self.stdout.write('结束同步')
