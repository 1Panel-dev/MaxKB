# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py
    @date：2024/3/14 11:54
    @desc:
"""
from .client_access_num_job import *
from .clean_chat_job import *
from .clean_debug_file_job import *


def run():
    client_access_num_job.run()
    clean_chat_job.run()
    clean_debug_file_job.run()
