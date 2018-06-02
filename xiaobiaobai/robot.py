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

robot = WeRoBot(token='lylinux', enable_session=True)
robot.config['SESSION_STORAGE'] = FileStorage(filename='werobot_session')

