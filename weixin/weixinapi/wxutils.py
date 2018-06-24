#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: wxutils.py
@time: 2018/6/9 上午12:05
"""


class Map(dict):
    """
    提供字典的dot访问模式
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        v = Map(v)
                    self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    v = Map(v)
                self[k] = v

    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getitem__(self, key):
        if key not in self.__dict__:
            super(Map, self).__setitem__(key, {})
            self.__dict__.update({key: Map()})
        return self.__dict__[key]

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


class WeixinError(Exception):

    def __init__(self, msg):
        super(WeixinError, self).__init__(msg)


class WeixinLoginError(WeixinError):

    def __init__(self, msg):
        super(WeixinLoginError, self).__init__(msg)


class WeixinPayError(WeixinError):

    def __init__(self, msg):
        super(WeixinPayError, self).__init__(msg)


class WXPayConstants(object):
    # SUCCESS, FAIL
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"

    # 签名类型
    SIGN_TYPE_HMACSHA256 = "HMAC-SHA256"
    SIGN_TYPE_MD5 = "MD5"

    # 字段
    FIELD_SIGN = "sign"
    FIELD_SIGN_TYPE = "sign_type"

    # URL
    MICROPAY_URL = "https://api.mch.weixin.qq.com/pay/micropay"
    UNIFIEDORDER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    ORDERQUERY_URL = "https://api.mch.weixin.qq.com/pay/orderquery"
    REVERSE_URL = "https://api.mch.weixin.qq.com/secapi/pay/reverse"
    CLOSEORDER_URL = "https://api.mch.weixin.qq.com/pay/closeorder"
    REFUND_URL = "https://api.mch.weixin.qq.com/secapi/pay/refund"
    REFUNDQUERY_URL = "https://api.mch.weixin.qq.com/pay/refundquery"
    DOWNLOADBILL_URL = "https://api.mch.weixin.qq.com/pay/downloadbill"
    REPORT_URL = "https://api.mch.weixin.qq.com/payitil/report"
    SHORTURL_URL = "https://api.mch.weixin.qq.com/tools/shorturl"
    AUTHCODETOOPENID_URL = "https://api.mch.weixin.qq.com/tools/authcodetoopenid"

    # Sandbox URL
    SANDBOX_MICROPAY_URL = "https://api.mch.weixin.qq.com/sandboxnew/pay/micropay"
    SANDBOX_UNIFIEDORDER_URL = "https://api.mch.weixin.qq.com/sandboxnew/pay/unifiedorder"
    SANDBOX_ORDERQUERY_URL = "https://api.mch.weixin.qq.com/sandboxnew/pay/orderquery"
    SANDBOX_REVERSE_URL = "https://api.mch.weixin.qq.com/sandboxnew/secapi/pay/reverse"
    SANDBOX_CLOSEORDER_URL = "https://api.mch.weixin.qq.com/sandboxnew/pay/closeorder"
    SANDBOX_REFUND_URL = "https://api.mch.weixin.qq.com/sandboxnew/secapi/pay/refund"
    SANDBOX_REFUNDQUERY_URL = "https://api.mch.weixin.qq.com/sandboxnew/pay/refundquery"
    SANDBOX_DOWNLOADBILL_URL = "https://api.mch.weixin.qq.com/sandboxnew/pay/downloadbill"
    SANDBOX_REPORT_URL = "https://api.mch.weixin.qq.com/sandboxnew/payitil/report"
    SANDBOX_SHORTURL_URL = "https://api.mch.weixin.qq.com/sandboxnew/tools/shorturl"
    SANDBOX_AUTHCODETOOPENID_URL = "https://api.mch.weixin.qq.com/sandboxnew/tools/authcodetoopenid"


class WeiXinConfig(object):
    def __init__(self, app_id, app_secret, mch_id, mch_key, notify_url, remote_addr, redirect_uri, scope, token,
                 use_sandbox=False,
                 sign_type=WXPayConstants.SIGN_TYPE_MD5, key=None, cert=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.mch_id = mch_id
        self.mch_key = mch_key
        self.notify_url = notify_url
        self.use_sandbox = use_sandbox
        self.sign_type = sign_type
        self.remote_addr = remote_addr
        self.key = key
        self.cert = cert
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.token = token


def get_wx_config():
    try:
        from xiaobiaobai.utils import get_systemconfigs
        sysconfig = get_systemconfigs()
        config = WeiXinConfig(app_id=sysconfig.weixin_appid, app_secret=sysconfig.weixin_appsecret,
                              scope=sysconfig.wx_scope, redirect_uri=sysconfig.wx_redirect_uri,
                              mch_id=sysconfig.mch_id, mch_key=sysconfig.mch_key,
                              notify_url=sysconfig.pay_notify_url, token=sysconfig.wx_token,
                              remote_addr=sysconfig.wx_remote_addr)
        return config
    except Exception as e:
        from xiaobiaobai.utils import logger
        logger.error(e)
        return None
