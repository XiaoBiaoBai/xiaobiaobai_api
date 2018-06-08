#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: serializers.py.py
@time: 2018/6/3 下午10:17
"""
from rest_framework import serializers
from orders.models import OrderModel, BlessingModel


class OrderSerializer(serializers.Serializer):
    def validate(self, attrs):
        pass

    def update(self, instance, validated_data):
        instance.third_orderid = validated_data.get('third_orderid', instance.third_orderid)
        instance.save()
        return instance

    class Meta:
        model = OrderModel
        fields = ('id', 'third_orderid', 'third_orderchannel', 'usermodel', 'target_usermodel', 'txid', 'confirmations',
                  'block_height', 'block_hash', 'fee', 'city', 'candies_count', 'order_content', 'created_time',
                  'last_mod_time')
