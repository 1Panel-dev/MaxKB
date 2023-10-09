# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： file_util.py
    @date：2023/9/25 21:06
    @desc:
"""


def get_file_content(path):
    file = open(path, "r",
                encoding='utf-8')
    content = file.read()
    file.close()
    return content
