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
@time: 2018/6/17 下午5:12
"""

from rest_framework import serializers
from accounts.models import USER_SEX_CHOICE, UserModel


class UserModelSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=True)
    username = serializers.CharField(required=True)
    sex = serializers.ChoiceField(choices=USER_SEX_CHOICE, required=True)
    headimage = serializers.CharField(required=False)

    def update(self, instance, validated_data):
        user = UserModel.objects.get(id=validated_data.get('id'))
        user.username = validated_data.get("username")
        user.sex = validated_data.get("sex")
        user.headimage = validated_data.get("headimage")
        user.save()
        return user

    def create(self, validated_data):
        user = UserModel.objects.create(**validated_data)
        return user
