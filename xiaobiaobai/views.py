#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: views.py
@time: 2018/7/7 上午10:39
"""

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.views import exception_handler


def default_view(request):
    return HttpResponse("<center><h1>小表白api</h1></center>")
