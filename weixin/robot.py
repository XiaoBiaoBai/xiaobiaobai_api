#!/usr/bin/env python
# encoding: utf-8


"""
@version: ??
@author: liangliangyy
@license: MIT Licence 
@contact: liangliangyy@gmail.com
@site: https://www.lylinux.net/
@software: PyCharm
@file: robot.py
@time: 2018/6/2 下午8:02
"""

from werobot import WeRoBot
from werobot.session.filestorage import FileStorage
from weixin.weixinapi.wxutils import get_wx_config
import os
from django.conf import settings

if os.path.exists(os.path.join(settings.BASE_DIR, 'werobot_session')):
    os.remove(os.path.join(settings.BASE_DIR, 'werobot_session'))

wxconfig = get_wx_config()

robot = WeRoBot(token='' if wxconfig is None else wxconfig.token, enable_session=True)
robot.config['SESSION_STORAGE'] = FileStorage(filename='werobot_session')

robot.config['APP_ID'] = '' if wxconfig is None else wxconfig.app_id
robot.config['APP_SECRET'] = '' if wxconfig is None else wxconfig.app_secret
