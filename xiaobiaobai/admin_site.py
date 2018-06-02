#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: admin_site.py
@time: 2018/5/20 下午7:52
"""

from django.contrib.admin import AdminSite
from django.contrib.admin.models import LogEntry

from systemconfig.admin import SystemConfigAdmin
from systemconfig.models import SystemConfigMode
from xiaobiaobai.logentryadmin import LogEntryAdmin


class XiaoBiaoBaiAdminSite(AdminSite):
    site_header = '小表白 administration'
    site_title = '小表白 site admin'

    def __init__(self, name='admin'):
        super(XiaoBiaoBaiAdminSite, self).__init__(name)

    def has_permission(self, request):
        return request.user.is_superuser


admin_site = XiaoBiaoBaiAdminSite(name='admin')

admin_site.register(SystemConfigMode, SystemConfigAdmin)

admin_site.register(LogEntry, LogEntryAdmin)
