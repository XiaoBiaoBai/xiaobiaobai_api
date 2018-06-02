#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: weixin.py
@time: 2018/5/28 下午9:24
"""

from weixin.weixinconfig import WeiXinConfig
from weixin.weixinutils import WXPayConstants, WXPayUtil


class WeiXinPay():
    def __init__(self, config: WeiXinConfig):
        self.wx_config = config
