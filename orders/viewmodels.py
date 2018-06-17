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
from orders.models import OrderModel
from xiaobiaobai.utils import get_systemconfigs


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


class PostLoveSerializer(serializers.Serializer):
    usermodel = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(),
                                                   pk_field=serializers.UUIDField(format='hex'))
    target_usermodel = serializers.PrimaryKeyRelatedField(queryset=UserModel.objects.all(),
                                                          pk_field=serializers.UUIDField(format='hex'))
    candies_count = serializers.IntegerField(required=True)
    order_content = serializers.CharField(required=True, max_length=200)
    city = serializers.CharField(required=True, max_length=100)
    wx_prepayid = serializers.CharField(required=True, max_length=100)
