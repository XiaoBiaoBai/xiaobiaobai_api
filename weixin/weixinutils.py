#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: weixinutils.py
@time: 2018/5/28 下午9:37
"""
import hashlib
import requests
import uuid
import copy
import hmac
import xml.etree.ElementTree as ElementTree
from weixin.weixinconfig import WeiXinConfig

text_type = str
string_types = (str,)
xrange = range


def as_text(v):  ## 生成unicode字符串
    if v is None:
        return None
    elif isinstance(v, bytes):
        return v.decode('utf-8', errors='ignore')
    elif isinstance(v, str):
        return v
    else:
        raise ValueError('Unknown type %r' % type(v))


def is_text(v):
    return isinstance(v, text_type)


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


class WXPayUtil(object):
    @staticmethod
    def dict2xml(data):
        """dict to xml
        @:param data: Dictionary
        @:return: string
        """
        # return as_text( xmltodict.unparse({'xml': data_dict}, pretty=True) )
        root = ElementTree.Element('xml')
        for k in data:
            v = data[k]
            child = ElementTree.SubElement(root, k)
            child.text = str(v)
        return as_text(ElementTree.tostring(root, encoding='utf-8'))

    @staticmethod
    def xml2dict(xml_str):
        """xml to dict
        @:param xml_str: string in XML format
        @:return: Dictionary
        """
        # return xmltodict.parse(xml_str)['xml']
        root = ElementTree.fromstring(xml_str)
        assert as_text(root.tag) == as_text('xml')
        result = {}
        for child in root:
            tag = child.tag
            text = child.text
            result[tag] = text
        return result

    @staticmethod
    def generate_signature(data, key, sign_type=WXPayConstants.SIGN_TYPE_MD5):
        """生成签名
        :param data: dict
        :param key: string. API key
        :param sign_type: string
        :return string
        """
        key = as_text(key)
        data_key_list = data.keys()
        data_key_list = sorted(data_key_list)  # 排序！
        combine_str = as_text('')
        for k in data_key_list:
            v = data[k]
            if k == WXPayConstants.FIELD_SIGN:
                continue
            if v is None or len(str(v)) == 0:
                continue
            combine_str = combine_str + as_text(str(k)) + as_text('=') + as_text(str(v)) + as_text('&')
        combine_str = combine_str + as_text('key=') + key
        if sign_type == WXPayConstants.SIGN_TYPE_MD5:
            return WXPayUtil.md5(combine_str)
        elif sign_type == WXPayConstants.SIGN_TYPE_HMACSHA256:
            return WXPayUtil.hmacsha256(combine_str, key)
        else:
            raise Exception("Invalid sign_type: {}".format(sign_type))

    @staticmethod
    def is_signature_valid(data, key, sign_type=WXPayConstants.SIGN_TYPE_MD5):
        """ 验证xml中的签名
        :param data: dict
        :param key: string. API key
        :param sign_type: string
        :return: bool
        """
        if WXPayConstants.FIELD_SIGN not in data:
            return False
        sign = WXPayUtil.generate_signature(data, key, sign_type)
        if sign == data[WXPayConstants.FIELD_SIGN]:
            return True
        return False

    @staticmethod
    def generate_signed_xml(data, key, sign_type=WXPayConstants.SIGN_TYPE_MD5):
        """ 生成带有签名的xml
        :param data: dict
        :param key: string. API key
        :param sign_type: string
        :return: xml
        """
        key = as_text(key)
        new_data_dict = copy.deepcopy(data)
        sign = WXPayUtil.generate_signature(data, key, sign_type)
        new_data_dict[WXPayConstants.FIELD_SIGN] = sign
        return WXPayUtil.dict2xml(new_data_dict)

    @staticmethod
    def generate_nonce_str():
        """ 生成随机字符串
        :return string
        """
        r = uuid.uuid1().hex.replace('-', '')
        return as_text(r)

    @staticmethod
    def md5(source):
        """ generate md5 of source. the result is Uppercase and Hexdigest.
        @:param source: string
        @:return: string
        """
        hash_md5 = hashlib.md5(as_text(source).encode('utf-8'))
        return hash_md5.hexdigest().upper()

    @staticmethod
    def hmacsha256(source, key):
        """ generate hmacsha256 of source. the result is Uppercase and Hexdigest.
        @:param source: string
        @:param key: string
        @:return: string
        """
        return hmac.new(as_text(key).encode('utf-8'), as_text(source).encode('utf-8'),
                        hashlib.sha256).hexdigest().upper()
