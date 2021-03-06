#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: wxpay.py
@time: 2018/6/9 上午12:06
"""
import random
import hashlib
import string
from xml.etree import cElementTree as etree
import time
import json
import requests
from xiaobiaobai.utils import cache_decorator
from weixin.weixinapi.wxutils import WeixinPayError, WeixinError, Map, WXPayConstants, WeiXinConfig
from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)


class WeixinPay(object):

    def __init__(self, config: WeiXinConfig):
        self.wxconfig = config
        self.sess = requests.Session()

    @property
    def nonce_str(self):
        char = string.ascii_letters + string.digits
        return "".join(random.choice(char) for _ in range(32))

    def sign(self, raw):
        raw = [(k, str(raw[k]) if isinstance(raw[k], int) else raw[k])
               for k in sorted(raw.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        s += "&key={0}".format(self.wxconfig.mch_key)
        return hashlib.md5(s.encode("utf-8")).hexdigest().upper()

    def check(self, data):
        sign = data.pop("sign")
        return sign == self.sign(data)

    def to_xml(self, raw):
        s = ""
        for k, v in raw.items():
            s += "<{0}>{1}</{0}>".format(k, v)
        s = "<xml>{0}</xml>".format(s)
        return s.encode("utf-8")

    def to_dict(self, content):
        raw = {}
        root = etree.fromstring(content)
        for child in root:
            raw[child.tag] = child.text
        return raw

    def _fetch(self, url, data, use_cert=False):
        data.setdefault("appid", self.wxconfig.app_id)
        data.setdefault("mch_id", self.wxconfig.mch_id)
        data.setdefault("nonce_str", self.nonce_str)
        data.setdefault("sign", self.sign(data))

        if use_cert:
            resp = self.sess.post(url, data=self.to_xml(data), cert=(self.wxconfig.cert, self.wxconfig.key))
        else:
            resp = self.sess.post(url, data=self.to_xml(data))
        content = resp.content.decode("utf-8")
        if "return_code" in content:
            data = Map(self.to_dict(content))
            if data.return_code == WXPayConstants.FAIL:
                raise WeixinPayError(data.return_msg)
            if "result_code" in content and data.result_code == WXPayConstants.FAIL:
                raise WeixinPayError(data.err_code_des)
            return data
        return content

    def reply(self, msg, ok=True):
        code = WXPayConstants.SUCCESS if ok else WXPayConstants.FAIL
        return self.to_xml(dict(return_code=code, return_msg=msg))

    def unified_order(self, **data):
        """
        统一下单
        out_trade_no、body、total_fee、trade_type必填
        app_id, mchid, nonce_str自动填写
        spbill_create_ip 在flask框架下可以自动填写, 非flask框架需要主动传入此参数
        """
        url = "https://api.mch.weixin.qq.com/pay/unifiedorder"

        # 必填参数
        if "out_trade_no" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数out_trade_no")
        if "body" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数body")
        if "total_fee" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数total_fee")
        if "trade_type" not in data:
            raise WeixinPayError("缺少统一支付接口必填参数trade_type")

        # 关联参数
        if data["trade_type"] == "JSAPI" and "openid" not in data:
            raise WeixinPayError("trade_type为JSAPI时，openid为必填参数")
        if data["trade_type"] == "NATIVE" and "product_id" not in data:
            raise WeixinPayError("trade_type为NATIVE时，product_id为必填参数")
        data.setdefault("notify_url", self.wxconfig.notify_url)
        if "spbill_create_ip" not in data:
            data.setdefault("spbill_create_ip", self.wxconfig.remote_addr)

        raw = self._fetch(url, data)
        logger.info(raw)
        return raw

    def jsapi(self, **kwargs):
        """
        生成给JavaScript调用的数据
        详细规则参考 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=7_7&index=6
        """
        kwargs.setdefault("trade_type", "JSAPI")
        raw = self.unified_order(**kwargs)
        package = "prepay_id={0}".format(raw["prepay_id"])
        timestamp = str(int(time.time()))
        nonce_str = self.nonce_str
        raw = dict(appId=self.wxconfig.app_id, timeStamp=timestamp,
                   nonceStr=nonce_str, package=package, signType="MD5")
        sign = self.sign(raw)
        return dict(package=package, appId=self.wxconfig.app_id, signType="MD5",
                    timeStamp=timestamp, nonceStr=nonce_str, sign=sign)

    def order_query(self, **data):
        """
        订单查询
        out_trade_no, transaction_id至少填一个
        appid, mchid, nonce_str不需要填入
        """
        url = "https://api.mch.weixin.qq.com/pay/orderquery"

        if "out_trade_no" not in data and "transaction_id" not in data:
            raise WeixinPayError("订单查询接口中，out_trade_no、transaction_id至少填一个")

        return self._fetch(url, data)

    def close_order(self, out_trade_no, **data):
        """
        关闭订单
        out_trade_no必填
        appid, mchid, nonce_str不需要填入
        """
        url = "https://api.mch.weixin.qq.com/pay/closeorder"

        data.setdefault("out_trade_no", out_trade_no)

        return self._fetch(url, data)

    def refund(self, **data):
        """
        申请退款
        out_trade_no、transaction_id至少填一个且
        out_refund_no、total_fee、refund_fee、op_user_id为必填参数
        appid、mchid、nonce_str不需要填入
        """
        if not self.wxconfig.key or not self.wxconfig.cert:
            raise WeixinError("退款申请接口需要双向证书")
        url = "https://api.mch.weixin.qq.com/secapi/pay/refund"
        if "out_trade_no" not in data and "transaction_id" not in data:
            raise WeixinPayError("退款申请接口中，out_trade_no、transaction_id至少填一个")
        if "out_refund_no" not in data:
            raise WeixinPayError("退款申请接口中，缺少必填参数out_refund_no")
        if "total_fee" not in data:
            raise WeixinPayError("退款申请接口中，缺少必填参数total_fee")
        if "refund_fee" not in data:
            raise WeixinPayError("退款申请接口中，缺少必填参数refund_fee")

        return self._fetch(url, data, True)

    def refund_query(self, **data):
        """
        查询退款
        提交退款申请后，通过调用该接口查询退款状态。退款有一定延时，
        用零钱支付的退款20分钟内到账，银行卡支付的退款3个工作日后重新查询退款状态。
        out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个
        appid、mchid、nonce_str不需要填入
        """
        url = "https://api.mch.weixin.qq.com/pay/refundquery"
        if "out_refund_no" not in data and "out_trade_no" not in data \
                and "transaction_id" not in data and "refund_id" not in data:
            raise WeixinPayError("退款查询接口中，out_refund_no、out_trade_no、transaction_id、refund_id四个参数必填一个")

        return self._fetch(url, data)

    def download_bill(self, bill_date, bill_type="ALL", **data):
        """
        下载对账单
        bill_date、bill_type为必填参数
        appid、mchid、nonce_str不需要填入
        """
        url = "https://api.mch.weixin.qq.com/pay/downloadbill"
        data.setdefault("bill_date", bill_date)
        data.setdefault("bill_type", bill_type)

        if "bill_date" not in data:
            raise WeixinPayError("对账单接口中，缺少必填参数bill_date")

        return self._fetch(url, data)

    
    def get_access_token(self):
        key='wx_access_token'
        value=cache.get(key)
        if value:
            logger.info('get_access_token hits cache')
            return value
        else: 
            url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={appid}&secret={secret}'.format(
                appid=self.wxconfig.app_id, secret=self.wxconfig.app_secret)
            rsp = requests.get(url)
            if rsp.status_code == 200:
                logger.info(rsp.content)
                obj = json.loads(rsp.content)
                value= obj['access_token']
                cache.set(key,value,7100)
                return value
            else:
                logger.error(rsp.text)

    def get_jsapi_ticket(self):
        key='jsapi_ticket'
        value=cache.get(key)
        if value:
            logger.info('jsapi_ticket hits cache')
            return value
        else: 
            token = self.get_access_token()
            url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={token}&type=jsapi'.format(token=token)
            rsp = requests.get(url)
            if rsp.status_code == 200:
                logger.info(rsp.content)
                obj = json.loads(rsp.content)
                value =  obj['ticket']
                cache.set(key,value,7100)
                return value
            else:
                logger.error(rsp.text)

    def jsapisign(self, raw):
        raw = [(k, str(raw[k]) if isinstance(raw[k], int) else raw[k])
               for k in sorted(raw.keys())]
        s = "&".join("=".join(kv) for kv in raw if kv[1])
        # s += "&key={0}".format(self.wxconfig.mch_key)
        return hashlib.sha1(s.encode("utf-8")).hexdigest()

    def create_wxconfig_sign(self, url: str):

        timestamp = str(int(time.time()))
        noncestr = self.nonce_str

        jsapi_ticket = self.get_jsapi_ticket()
        logger.info(jsapi_ticket)
        data = {'url': url}
        data['timestamp'] = timestamp
        data['jsapi_ticket'] = jsapi_ticket

        data['noncestr'] = noncestr
        logger.info(json.dumps({
            'jsapi_ticket':jsapi_ticket,
            'noncestr':noncestr,
            'timestamp':timestamp

        }))
        sign = self.jsapisign(data)
        logger.info(sign)
        jsapidata = {}
        jsapidata.setdefault('debug', 'true')
        jsapidata.setdefault('appId', self.wxconfig.app_id)
        jsapidata.setdefault('timestamp', timestamp)
        jsapidata.setdefault('nonceStr', noncestr)
        jsapidata.setdefault('signature', sign)
        jsapidata['jsApiList'] = [
            'checkJsApi',
            'onMenuShareTimeline',
            'onMenuShareAppMessage',
            'onMenuShareQQ',
            'onMenuShareWeibo',
            'onMenuShareQZone',
            'hideMenuItems',
            'showMenuItems',
            'hideAllNonBaseMenuItem',
            'showAllNonBaseMenuItem',
            'translateVoice',
            'startRecord',
            'stopRecord',
            'onVoiceRecordEnd',
            'playVoice',
            'onVoicePlayEnd',
            'pauseVoice',
            'stopVoice',
            'uploadVoice',
            'downloadVoice',
            'chooseImage',
            'previewImage',
            'uploadImage',
            'downloadImage',
            'getNetworkType',
            'openLocation',
            'getLocation',
            'hideOptionMenu',
            'showOptionMenu',
            'closeWindow',
            'scanQRCode',
            'chooseWXPay',
            'openProductSpecificView',
            'addCard',
            'chooseCard',
            'openCard'
        ]
        return jsapidata

