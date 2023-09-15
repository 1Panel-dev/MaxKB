# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： users.py
    @date：2023/9/4 10:09
    @desc:
"""
import hashlib

from django.db import models

__all__ = ["User", "password_encrypt"]


def password_encrypt(raw_password):
    """
    密码 md5加密
    :param raw_password: 密码
    :return:  加密后密码
    """
    md5 = hashlib.md5()  # 2，实例化md5() 方法
    md5.update(raw_password.encode())  # 3，对字符串的字节类型加密
    result = md5.hexdigest()  # 4，加密
    return result


class User(models.Model):
    email = models.EmailField(unique=True, verbose_name="邮箱")
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=150, verbose_name="密码")
    role = models.CharField(max_length=150, verbose_name="角色")
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"

    def set_password(self, raw_password):
        self.password = password_encrypt(raw_password)
        self._password = raw_password
