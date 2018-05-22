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

from systemconfig.models import SystemConfigMode

logger = logging.getLogger('xiaobiaobai')


def get_systemconfigs():
    o = SystemConfigMode.objects.first()
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
