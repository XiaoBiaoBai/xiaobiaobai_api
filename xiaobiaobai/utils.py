#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: utils.py
@time: 2018/5/20 下午7:17
"""
import logging
from bitcash import Key
import requests
import json
import uuid
import qrcode
from django.conf import settings
from django.core.cache import cache
from hashlib import md5

from systemconfig.models import SystemConfigMode

logger = logging.getLogger('xiaobiaobai')


def send_bitcash_message(message):
    if len(message.encode('utf-8')) > 213:
        raise ValueError(message + "超长，长度是:" + len(message.encode('utf-8')))
    else:
        config = get_systemconfigs()
        key = Key(config.private_key)
        upspents = key.get_unspents()
        logger.info(upspents)
        logger.info(key.address)
        outputs = [
            (config.outaddress, 10056, 'satoshi'),
        ]
        try:
            txhash, txid = key.send(outputs, message=message, fee=config.default_fee)
            logging.info('{m}交易成功,txid:{txid}'.format(m=message, txid=txid))
            return (txhash, txid)
        except Exception as e:
            logging.error('{m}交易失败,异常:{e}'.format(m=message, e=str(e)))
            raise e


def get_transaction_info(txid):
    api = 'https://bch-chain.api.btc.com/v3/tx/' + txid
    response = requests.get(api)
    if response.status_code == 200:
        result = json.loads(response.text, encoding='utf-8')
        return result


def get_baidu_accesstoken():
    config = get_systemconfigs()
    # logger.info(config.baidu_appid, config.baidu_appsecret)
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={clientid}&client_secret={secret}'.format(
        clientid=config.baidu_appid, secret=config.baidu_appsecret)
    response = requests.get(host)
    logger.info(response.text)
    return response.text


def check_words_spam(content):
    try:
        accesstoken = get_baidu_accesstoken()
        url = 'https://aip.baidubce.com/rest/2.0/antispam/v2/spam?access_token=' + accesstoken
        d = {
            'content': content
        }
        rsp = requests.post(url, d)
        logger.info(rsp.text)
        obj = json.loads(rsp.text)
        return obj and obj['result'] and obj['result']['spam'] == 0
    except Exception as e:
        logger.error(e)
        return True


def convert_to_uuid(s: str):
    try:
        u = uuid.UUID(str(s))
        return u
    except Exception as e:
        return None


def create_qr_code(body: str):
    image = qrcode.make(body)
    return image


def cache_decorator(expiration=3 * 60):
    def wrapper(func):
        def news(*args, **kwargs):
            key = ''
            try:
                view = args[0]
                key = view.get_cache_key()
            except:
                key = None
                pass
            if not key:
                unique_str = repr((func, args, kwargs))

                m = md5(unique_str.encode('utf-8'))
                key = m.hexdigest()
            value = cache.get(key)
            if value:
                logger.info('cache_decorator get cache:%s key:%s' % (func.__name__, key))
                return value
            else:
                logger.info('cache_decorator set cache:%s key:%s' % (func.__name__, key))
                value = func(*args, **kwargs)
                cache.set(key, value, expiration)
                return value

        return news


@cache_decorator
def get_systemconfigs():
    o = SystemConfigMode.objects.first()
    if not o:
        raise ValueError("系统配置不能为空")
    if settings.DEBUG:
        pass
        # logger.info(repr(o))
    return o


class ResponseCode():
    SUCCESS = 200,
    ERROR = 500
    NOT_FOUND = 404
    FORBIDDEN = 403
    WX_ERROR = 501
