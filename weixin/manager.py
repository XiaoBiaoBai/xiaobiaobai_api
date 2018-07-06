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
@time: 2018/6/9 上午12:59
"""

from accounts.models import WxUserModel, UserModel
from django.utils.timezone import now

from weixin.weixinapi.wxpay import WeixinPay

from weixin.weixinapi.wxlogin import WeixinLogin
from weixin.weixinapi.wxutils import get_wx_config, WeixinLoginError

from accounts.models import WxUserModel
from orders.models import OrderModel
from xiaobiaobai.signals import post_love_word_signal
import uuid
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)


def get_wx_pay_client():
    wxconfig = get_wx_config()

    pay_client = WeixinPay(wxconfig)
    return pay_client


class WxManager():
    @staticmethod
    def wxlogin_with_createuser(token_response):
        '''
        根据微信openid创建或获取用户
        :param token_response:微信返回token
        :return:(openid,usermodel.id)
        '''
        openid = token_response['openid']
        try:
            wxuser = WxUserModel.objects.get(openid=openid)
        except ObjectDoesNotExist:
            wxuser = WxUserModel()
            wxuser.openid = openid

        wxuser.access_token = token_response['access_token']
        wxuser.expires_in = token_response['expires_in']
        wxuser.refresh_token = token_response['refresh_token']
        wxuser.last_login_time = now()
        wxuser.save()
        try:
            usermodel = UserModel.objects.get(wxusermodel__openid=openid)
        except ObjectDoesNotExist:
            usermodel = UserModel()

        return (openid, usermodel.id)

    @staticmethod
    def create_wx_jsapi(openid: str, orderid: uuid.UUID, body: str, fee: int):
        data = {'out_trade_no': orderid.hex, 'body': body, 'total_fee': fee, 'trade_type': 'JSAPI',
                'openid': openid};
        pay_client = get_wx_pay_client()
        result = pay_client.jsapi(**data)
        logger.info(result)
        return result

    @staticmethod
    def create_wx_order(openid: str, orderid: uuid.UUID, body: str, fee: int):
        data = {'out_trade_no': orderid.hex, 'body': body, 'total_fee': fee, 'trade_type': 'JSAPI',
                'openid': openid};
        pay_client = get_wx_pay_client()
        result = pay_client.unified_order(**data)
        logger.info(result)
        return result

    @staticmethod
    def wx_pay_callback(data):
        out_trade_no = data["out_trade_no"]
        try:
            order = OrderModel.objects.get(id=out_trade_no)
            order.third_orderid = data["transaction_id"]
            order.order_status = 'p'
            order.pay_time = now()
            order.save()
            post_love_word_signal.send(sender=WxManager.__class__, orderid=order.id)
            # from orders.manager import OrderManager
            # result = OrderManager.post_love_words(order.order_content)
            # if result:
            #     txhash, txid = result
            #     order.txid = txid
            #     order.tx_hex = txhash
            #     order.save()
            #     return True
            return True
        except OrderModel.DoesNotExist:
            logger.error('微信支付回调，订单未找到.out_trade_no:{out_trade_no}'.format(out_trade_no=out_trade_no))
            raise

    @staticmethod
    def create_wxconfig_sign(url):
        pay_client = get_wx_pay_client()
        return pay_client.create_wxconfig_sign(url)
