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

from orders.viewmodels import PostLoveSerializer, BlessingSerializer
from weixin.manager import WxManager
from orders.models import OrderModel, BlessingModel
from accounts.models import UserModel
from xiaobiaobai.utils import send_bitcash_message, cache_decorator
import logging

logger = logging.getLogger(__name__)


class OrderManager():
    @staticmethod
    def calculate_order_fee(order: PostLoveSerializer):
        from xiaobiaobai.utils import get_systemconfigs
        sysconfig = get_systemconfigs()
        return sysconfig.default_fee

    @staticmethod
    def post_love_words(content: str):
        try:
            txhash, txid = send_bitcash_message(content)
            logger.info("txhash:{txhash}.txid:{txid}".format(txhash=txhash, txid=txid))
            return (txhash, txid)
        except Exception as e:
            logger.error(e)
            return None

    @staticmethod
    def create_order(order: PostLoveSerializer):
        data = order.data
        ordermodel = OrderModel()
        ordermodel.order_content = data['order_content']
        ordermodel.usermodel = UserModel.objects.get(pk=data['usermodel'])
        ordermodel.username = data['username']
        ordermodel.target_username = data['target_username']
        ordermodel.city = data['city']
        ordermodel.background_img = data['background_img'] if 'background_img' in data else ''
        ordermodel.fee = OrderManager.calculate_order_fee(order)

        ordermodel.save()
        openid = ordermodel.usermodel.wxusermodel.openid

        jsdata = WxManager.create_wx_jsapi(openid=openid, orderid=ordermodel.id, body="区块链表白",
                                           fee=ordermodel.fee)

        return (ordermodel, jsdata)

    @staticmethod
    def create_blessing_order(order: BlessingSerializer):
        ordermodel = order.data['ordermodel']
        usermodel = order.data['usermodel']
        o = OrderModel.objects.get(pk=ordermodel)
        u = UserModel.objects.get(pk=usermodel)
        b = BlessingModel()
        b.usermodel = u
        b.ordermodel = o
        b.save()

    @staticmethod
    @cache_decorator(1 * 60)
    def get_confessionwall_counts():
        return OrderModel.objects.filter(show_confession_wall=True).filter(order_status='p').count()

    @staticmethod
    def update_show_confession_wall(userid, orderid, status: bool):
        order = OrderModel.objects.get(id=orderid)
        user = UserModel.objects.get(id=userid)
        if order.usermodel.id != user.id:
            raise ValueError("用户非法")
        order.show_confession_wall = status
        order.save()
