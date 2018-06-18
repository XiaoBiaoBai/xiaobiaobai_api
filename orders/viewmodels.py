#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: viewmodels.py
@time: 2018/6/9 上午1:28
"""
from rest_framework import serializers
from accounts.models import UserModel, WxUserModel
from orders.models import OrderModel, BlessingModel
from xiaobiaobai.utils import get_systemconfigs, logger

from django.core.exceptions import ObjectDoesNotExist

from accounts.viewmodels import UserModelSerializer


# class PostLoveSerializer(serializers.Serializer):
#     content = serializers.CharField(required=True, max_length=200)
#     post_userid = serializers.UUIDField(required=True)
#     target_userid = serializers.UUIDField(required=True)
#     location = serializers.CharField(required=False)
#     candy_count = serializers.IntegerField(required=True)
#     post_user_openid = serializers.CharField(required=True)
#
#     def validate(self, attrs):
#         post_userid = attrs['post_userid']
#         target_userid = attrs['target_userid']
#         post_user_openid = attrs['post_user_openid']
#         try:
#             m = UserModel.objects.get(id == post_userid)
#             if m.wxusermodel.openid != post_user_openid:
#                 raise serializers.ValidationError("post_user_openid非法")
#         except UserModel.DoesNotExist:
#             raise serializers.ValidationError("post_userid不存在")
#
#         try:
#             UserModel.objects.get(id == target_userid)
#         except UserModel.DoesNotExist:
#             raise serializers.ValidationError("post_userid不存在")
#
#         return super(PostLoveSerializer, self).validate(attrs)


class BlessingSerializer(serializers.Serializer):
    usermodel = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(),
                                                   pk_field=serializers.UUIDField())
    ordermodel = serializers.PrimaryKeyRelatedField(queryset=OrderModel.objects.all(),
                                                    pk_field=serializers.UUIDField())

    # def validate(self, attrs):
    #     logger.info(attrs)
    #     usermodel = attrs['usermodel']
    #     ordermodel = attrs['ordermodel']
    #     try:
    #         UserModel.objects.get(pk=usermodel.id)
    #     except ObjectDoesNotExist:
    #         raise serializers.ValidationError("用户不存在")
    #     try:
    #         OrderModel.objects.get(pk=ordermodel)
    #     except ObjectDoesNotExist:
    #         raise serializers.ValidationError("订单信息不存在")


class PostLoveSerializer(serializers.Serializer):
    usermodel = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(),
                                                   pk_field=serializers.UUIDField())
    target_usermodel = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(),
                                                          pk_field=serializers.UUIDField())
    candies_count = serializers.IntegerField(required=True, min_value=0)
    order_content = serializers.CharField(required=True, max_length=200)
    city = serializers.CharField(required=True, max_length=100)
    wx_prepayid = serializers.CharField(required=True, max_length=100)

    def validate(self, attrs):
        usermodel = attrs['usermodel']
        target_usermodel = attrs['target_usermodel']
        try:
            UserModel.objects.get(pk=usermodel)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("用户不存在")
        try:
            UserModel.objects.get(pk=target_usermodel)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("目标用户不存在")


class OrderSerializer(serializers.Serializer):
    id = serializers.UUIDField(format='hex')
    usermodel = UserModelSerializer(read_only=True)
    target_usermodel = UserModelSerializer(read_only=True)

    candies_count = serializers.IntegerField(required=True, min_value=0)
    order_content = serializers.CharField(required=True, max_length=200)
    city = serializers.CharField(required=True, max_length=100)
    wx_prepayid = serializers.CharField(required=True, max_length=100)
    blessings = BlessingSerializer(read_only=True, many=True, source='blessingmodel_set')
