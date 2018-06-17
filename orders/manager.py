#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: manager.py
@time: 2018/6/9 下午9:24
"""

from orders.viewmodels import PostLoveSerializer
from weixin.manager import WxManager
from orders.models import OrderModel
from accounts.models import UserModel
from xiaobiaobai.utils import send_bitcash_message, logger


class OrderManager():
    @staticmethod
    def calculate_order_fee(order: PostLoveSerializer):
        return 100

    @staticmethod
    def post_love_words(content: str):
        try:
            txhash, txid = send_bitcash_message(content)
            logger.info()
            return (txhash, txid)
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def create_order(order: PostLoveSerializer):
        ordermodel = OrderModel()
        ordermodel.order_content = order.order_content
        ordermodel.usermodel = UserModel.objects.get(pk=order.usermodel)
        ordermodel.target_usermodel = UserModel.objects.get(pk=order.target_usermodel)
        ordermodel.city = order.city
        ordermodel.fee = OrderManager.calculate_order_fee(order)

        ordermodel.save()
        openid = ordermodel.usermodel.wxusermodel.openid

        jsdata = WxManager.create_wx_jsapi(openid=openid, orderid=ordermodel.id, body="发布表白",
                                           fee=ordermodel.fee)
        return (ordermodel, jsdata)
