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

from systemconfig.models import SystemConfigMode

logger = logging.getLogger('xiaobiaobai')


def get_systemconfigs():
    o = SystemConfigMode.objects.first()
    if not o:
        raise ValueError("系统配置不能为空")
    return o


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
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={clientid}&client_secret={secret}'.format(
        clientid=config.baidu_appid, secret=config.baidu_appsecret)
    response = requests.get(host)
    return response.content


def check_words_spam(content):
    accesstoken = get_baidu_accesstoken()


def convert_to_uuid(s: str):
    try:
        u = uuid.UUID(s)
        return u
    except Exception as e:
        return None


def create_qr_code(body: str):
    image = qrcode.make(body)
    return image


class ResponseCode():
    SUCCESS = 200,
    ERROR = 500
    NOT_FOUND = 404
    FORBIDDEN = 403
    WX_ERROR = 501
