#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: weixinconfig.py
@time: 2018/5/28 下午9:25
"""
from weixin.weixinutils import WXPayConstants


class WeiXinConfig(object):
    def __init__(self, app_id, mch_id, mch_key, notify_url, use_sandbox=False, sign_type=WXPayConstants.SIGN_TYPE_MD5):
        self.app_id = app_id
        self.mch_id = mch_id
        self.mch_key = mch_key
        self.notify_url = notify_url
        self.use_sandbox = use_sandbox
        self.sign_type = sign_type
