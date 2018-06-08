#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: wxlogin.py
@time: 2018/6/9 上午12:00
"""
import requests
import json

from weixin.weixinapi.wxutils import WeixinError, WeixinLoginError, Map, WeiXinConfig


class WeixinLogin(object):

    def __init__(self, wxconfig: WeiXinConfig):
        self.sess = requests.Session()
        self.wxconfig = wxconfig

    def _get(self, url, params):
        resp = self.sess.get(url, params=params)
        data = Map(json.loads(resp.content.decode("utf-8")))
        if data.errcode:
            msg = "%(errcode)d %(errmsg)s" % data
            raise WeixinLoginError(msg)
        return data

    def authorize(self, state=None):
        """
        生成微信认证地址并且跳转
        :param state: 认证成功后会原样带上此字段
        """
        url = "https://open.weixin.qq.com/connect/oauth2/authorize"
        assert self.wxconfig.scope in ["snsapi_base", "snsapi_userinfo"]
        data = dict()
        data.setdefault("appid", self.wxconfig.app_id)
        data.setdefault("redirect_uri", self.wxconfig.redirect_uri)
        data.setdefault("response_type", "code")
        data.setdefault("scope", self.wxconfig.scope)
        if state:
            data.setdefault("state", state)
        data = [(k, data[k]) for k in sorted(data.keys()) if data[k]]
        s = "&".join("=".join(kv) for kv in data if kv[1])
        return "{0}?{1}".format(url, s)

    def access_token(self, code):
        """
        获取令牌
        """
        url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        args = dict()
        args.setdefault("appid", self.wxconfig.app_id)
        args.setdefault("secret", self.wxconfig.app_secret)
        args.setdefault("code", code)
        args.setdefault("grant_type", "authorization_code")

        return self._get(url, args)

    def auth(self, access_token, openid):
        """
        检验授权凭证
        :param access_token: 授权凭证
        :param openid: 唯一id
        """
        url = "https://api.weixin.qq.com/sns/auth"
        args = dict()
        args.setdefault("access_token", access_token)
        args.setdefault("openid", openid)

        return self._get(url, args)

    def refresh_token(self, refresh_token):
        """
        重新获取access_token
        :param refresh_token: 刷新令牌
        """
        url = "https://api.weixin.qq.com/sns/oauth2/refresh_token"
        args = dict()
        args.setdefault("appid", self.wxconfig.app_id)
        args.setdefault("grant_type", "refresh_token")
        args.setdefault("refresh_token", refresh_token)

        return self._get(url, args)

    def userinfo(self, access_token, openid):
        """
        获取用户信息
        :param access_token: 令牌
        :param openid: 用户id，每个应用内唯一
        """
        url = "https://api.weixin.qq.com/sns/userinfo"
        args = dict()
        args.setdefault("access_token", access_token)
        args.setdefault("openid", openid)
        args.setdefault("lang", "zh_CN")

        return self._get(url, args)

    def user_info(self, access_token, openid):
        """
        获取用户信息
        兼容老版本0.3.0,与WeixinMP的user_info冲突
        """
        return self.userinfo(access_token, openid)

    def jscode2session(self, js_code):
        """
        小程序获取 session_key 和 openid
        """
        url = "https://api.weixin.qq.com/sns/jscode2session"
        args = dict()
        args.setdefault("appid", self.wxconfig.app_id)
        args.setdefault("secret", self.wxconfig.app_secret)
        args.setdefault("js_code", js_code)
        args.setdefault("grant_type", "authorization_code")
        return self._get(url, args)
