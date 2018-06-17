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

from xiaobiaobai.utils import logger
from accounts.models import WxUserModel
from orders.models import OrderModel
import uuid
from django.utils.timezone import now

wxconfig = get_wx_config()

pay_client = WeixinPay(wxconfig)


class WxManager():
    @staticmethod
    def wxlogin_with_createuser(token_response):
        '''
        根据微信openid创建用户及被表白用户
        :param token_response:微信返回token
        :return:(openid,usermodel.id,targetusermodel.id)
        '''
        openid = token_response['openid']
        wxuser = WxUserModel.objects.get_or_create(openid=openid)[0]
        wxuser.access_token = token_response['access_token']
        wxuser.expires_in = token_response['expires_in']
        wxuser.refresh_token = token_response['refresh_token']
        wxuser.last_login_time = now()
        wxuser.save()

        usermodel = UserModel.objects.get_or_create(WxUserModel.openid == openid)[0]

        targetusermodel = UserModel()
        targetusermodel.save()
        usermodel.targetusermodel = targetusermodel
        usermodel.save()

        return (openid, usermodel.id, targetusermodel.id)

    @staticmethod
    def create_wx_jsapi(openid: str, orderid: uuid.UUID, body: str, fee: int):
        data = {'out_trade_no': orderid.hex, 'body': body, 'total_fee': fee, 'trade_type': 'JSAPI',
                'openid': openid};
        result = pay_client.jsapi(**data)
        logger.info(result)
        return result

    @staticmethod
    def create_wx_order(openid: str, orderid: uuid.UUID, body: str, fee: int):
        data = {'out_trade_no': orderid.hex, 'body': body, 'total_fee': fee, 'trade_type': 'JSAPI',
                'openid': openid};
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
            return True
        except OrderModel.DoesNotExist:
            raise
