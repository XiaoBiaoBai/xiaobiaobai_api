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

wxconfig = get_wx_config()

robot = WeRoBot(token=wxconfig.token, enable_session=True)
robot.config['SESSION_STORAGE'] = FileStorage(filename='werobot_session')
robot.config['APP_ID'] = wxconfig.app_id
robot.config['APP_SECRET'] = wxconfig.app_secret
