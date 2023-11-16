# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py
    @date：2023/11/10 10:43
    @desc:
"""
from .listener_manage import *
from .listener_chat_message import *


def run():
    listener_manage.ListenerManagement().run()
    listener_chat_message.ListenerChatMessage().run()
