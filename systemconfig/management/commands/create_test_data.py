#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: create_test_data.py
@time: 2018/6/18 下午12:12
"""

import random

from django.core.management.base import BaseCommand, CommandError
from accounts.models import UserModel, WxUserModel
from orders.models import OrderModel, BlessingModel


class Command(BaseCommand):
    help = '创建测试数据'

    @property
    def random_number(self):
        d = random.randint(0, 10000)
        random.seed(d)
        return str(random.randint(0, 1000))

    def handle(self, *args, **options):
        wxuser = WxUserModel()

        wxuser.headimage = 'wee.jpg'
        wxuser.openid = 'openid11'
        wxuser.save()

        u = UserModel()
        u.sex = 'm'
        u.username = '啦啦啦' + self.random_number
        u.headimage = 'wcf.jpg'
        u.wxusermodel = wxuser

        u.save()

        t = UserModel()
        t.sex = 'w'
        t.username = '发发发' + self.random_number
        t.headimage = 'wcwf.jpg'
        t.save()

        o = OrderModel()

        o.usermodel = u
        o.target_usermodel = t
        o.order_content = '测试' + self.random_number
        o.candies_count = 1
        o.city = '上海'

        o.save()
        b = BlessingModel()
        b.usermodel = u
        b.ordermodel = o
        b.save()

        o.blessingmodel_set.add(b)
        o.save()

        self.stdout.write('成功创建测试数据')
