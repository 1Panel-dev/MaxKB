# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： compile.py
    @date：2024/12/23 14:11
    @desc:
"""
import os
import sys
import shutil
from py_compile import compile


def clean(path_str: str):
    for parent, dir_name, filename in os.walk(path_str):
        for dir_str in dir_name:
            if dir == '__pycache__':
                fullname = os.path.join(parent, dir_str)
                try:
                    shutil.rmtree(fullname)
                except Exception as e:
                    print("Can't clean Folder:%s, reason:%s" % (fullname, e))


def compile_pyc(path_str: str):
    for parent, dir_name, filename in os.walk(path_str):
        for cfile in filename:
            fullname = os.path.join(parent, cfile)
            if cfile[-3:] == '.py':
                try:
                    if compile(fullname):
                        if cfile != 'settings.py' and cfile != 'wsgi.py':
                            os.remove(fullname)  # 删除原文件，保留settings.py和wsgi.py
                    else:
                        print("Can't compile file:%s,The original file has been retained" % fullname)
                except Exception as e:
                    print("Can't compile file:%s, reason:%s" % (fullname, e))


def move(path_str: str):
    for parent, dir_name, filename in os.walk(path_str):
        for c_file in filename:
            fullname = os.path.join(parent, c_file)
            if c_file[-4:] == '.pyc':
                try:
                    if parent.endswith('__pycache__'):
                        parent_path = os.path.dirname(parent)
                        shutil.move(fullname, parent_path)
                except Exception as e:
                    print("Can't move file:%s, reason:%s" % (fullname, e))


def replace_name(path_str: str):
    for parent, dir_name, filename in os.walk(path_str):
        for c_file in filename:
            fullname = os.path.join(parent, c_file)
            if c_file[-4:] == '.pyc':
                try:
                    cfile_name = ''
                    cfile_list = c_file.split('.')
                    version = sys.version_info
                    replace_name_str = 'cpython-' + str(version[0]) + str(version[1])
                    for i in range(len(cfile_list)):
                        if cfile_list[i] == replace_name_str:
                            continue
                        cfile_name += cfile_list[i]
                        if i == len(cfile_list) - 1:
                            continue
                        cfile_name += '.'
                    shutil.move(fullname, os.path.join(parent, cfile_name))
                except Exception as e:
                    print("Can't remove file:%s, reason:%s" % (fullname, e))


if __name__ == '__main__':
    path = "/opt/maxkb/app/apps"
    clean(path)
    compile_pyc(path)
    move(path)
    replace_name(path)
    clean(path)
