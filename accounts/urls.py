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
@time: 2018/6/17 下午5:36
"""

from django.urls import path, re_path
from accounts.views import UserObjectApi, fileupload

app_name = "accounts"

urlpatterns = [
    path('usermodel/<str:pk>', UserObjectApi.as_view(), name="usermodel"),
    path('fileupload', fileupload, name='fileupload')
]
