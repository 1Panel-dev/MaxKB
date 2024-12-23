# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： compile.py
    @date：2024/12/23 14:11
    @desc:
"""
import os
from py_compile import compile


def compile_pyc(path_str: str):
    """
    将py编译为pyc文件
    @param path_str: 需要编译的目录
    @return: None
    """
    for parent, dir_name, filename in os.walk(path_str):
        for cfile in filename:
            fullname = os.path.join(parent, cfile)
            if cfile[-3:] == '.py':
                try:
                    if compile(fullname, fullname.replace('py', 'pyc')):
                        if cfile != 'settings.py' and cfile != 'wsgi.py':
                            os.remove(fullname)  # 删除原文件，保留settings.py和wsgi.py
                            print("Success compile and remove file:%s" % fullname)
                    else:
                        print("Can't compile file:%s,The original file has been retained" % fullname)
                except Exception as e:
                    print("Can't compile file:%s, reason:%s" % (fullname, e))


if __name__ == '__main__':
    compile_pyc("../apps")
