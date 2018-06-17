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
@time: 2018/6/10 下午12:16
"""

from django.urls import path
from orders import views

app_name = "orders"

urlpatterns = [
    path('submit', views.submit_lovecontent, name="submit_lovecontent"),
]
