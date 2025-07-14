# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 10:20
    @desc:
"""
import uuid_utils.compat as uuid

from django.db import models

from common.utils.common import password_encrypt


class User(models.Model):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid7, editable=False, verbose_name="主键id")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="邮箱", db_index=True)
    phone = models.CharField(max_length=20, verbose_name="电话", default="", db_index=True)
    nick_name = models.CharField(max_length=150, verbose_name="昵称", unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名", db_index=True)
    password = models.CharField(max_length=150, verbose_name="密码")
    role = models.CharField(max_length=150, verbose_name="角色")
    source = models.CharField(max_length=10, verbose_name="来源", default="LOCAL", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    language = models.CharField(max_length=10, verbose_name="语言", null=True, default=None)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True, db_index=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, null=True, db_index=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"

    def set_password(self, row_password):
        self.password = password_encrypt(row_password)
        self._password = row_password
