#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: urls.py
@time: 2018/6/10 下午12:04
"""

from django.urls import path
from weixin import views

from werobot.contrib.django import make_view
from weixin.robot import robot

app_name = "weixin"

urlpatterns = [
    path(r'wxlogin', views.wxuser_login, name="wxlogin"),
    path(r'paycallback/', views.wx_pay_callback, name="wx_pay_callback"),
    path(r'wxcallback', make_view(robot)),
    path(r'wx_sign', views.wx_sign, name="wx_sign"),
]
