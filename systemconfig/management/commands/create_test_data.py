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

from django.core.management.base import BaseCommand, CommandError
from accounts.models import UserModel, WxUserModel
from orders.models import OrderModel


class Command(BaseCommand):
    help = '创建测试数据'

    def handle(self, *args, **options):
        wxuser = WxUserModel()

        wxuser.headimage = 'wee.jpg'
        wxuser.openid = 'openid11'
        wxuser.save()

        u = UserModel()
        u.sex = 'm'
        u.username = '啦啦啦123'
        u.headimage = 'wcf.jpg'
        u.wxusermodel = wxuser

        u.save()

        t = UserModel()
        t.sex = 'w'
        t.username = '发发发'
        t.headimage = 'wcwf.jpg'
        t.save()

        o = OrderModel()

        o.usermodel = u
        o.target_usermodel = t
        o.order_content = '测试123'
        o.candies_count = 1
        o.city = '上海'
        o.save()

        self.stdout.write('成功创建测试数据')
