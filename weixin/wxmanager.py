#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: wxmanager.py
@time: 2018/6/9 上午12:59
"""

from accounts.models import WxUserModel, UserModel
from django.utils.timezone import now

from weixin.weixinapi.wxpay import WeixinPay

from weixin.weixinapi.wxlogin import WeixinLogin
from weixin.weixinapi.wxutils import get_wx_config, WeixinLoginError

from xiaobiaobai.utils import logger
from accounts.models import WxUserModel

wxconfig = get_wx_config()

pay_client = WeixinPay(wxconfig)


class WxManager():
    @staticmethod
    def wxlogin_with_createuser(token_response):
        openid = token_response['openid']
        wxuser = WxUserModel.objects.get_or_create(openid=openid)[0]
        wxuser.access_token = token_response['access_token']
        wxuser.expires_in = token_response['expires_in']
        wxuser.refresh_token = token_response['refresh_token']
        wxuser.last_login_time = now()
        wxuser.save()

        usermodel = UserModel.objects.get_or_create(WxUserModel.openid == openid)[0]
        WxManager.create_wx_order(openid)
        return (openid, usermodel.id)

    @staticmethod
    def create_wx_order(openid):
        data = {'out_trade_no': 'out_trade_no', 'body': '测试下单', 'total_fee': 1, 'trade_type': 'JSAPI',
                'openid': openid};
        result = pay_client.unified_order(**data)
        logger.info(result)
