#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: send_bch_message.py
@time: 2018/5/20 下午7:43
"""

from django.core.management.base import BaseCommand, CommandError
from xiaobiaobai.utils import send_bitcash_message


class Command(BaseCommand):
    help = '提交交易'

    def add_arguments(self, parser):
        parser.add_argument('message', type=str, help='输入交易信息')

    def handle(self, *args, **options):
        message = options['message']
        self.stdout.write('开始发送交易')
        try:
            result = send_bitcash_message(message)
            if result:
                txhash, txid = send_bitcash_message(message)
                self.stdout.write('交易提交成功，txid:' + txid)
                self.stdout.write('txhash:' + txhash)
        except Exception as e:
            self.stderr.write('交易失败，异常:' + str(e))
