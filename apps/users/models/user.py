# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： users.py
    @date：2023/9/4 10:09
    @desc:
"""
import hashlib
import os
import uuid

from django.db import models

from common.constants.permission_constants import Permission, Group, Operate
from common.db.sql_execute import select_list
from common.mixins.app_model_mixin import AppModelMixin
from common.util.file_util import get_file_content
from smartdoc.conf import PROJECT_DIR

__all__ = ["User", "password_encrypt", 'get_user_dynamics_permission']


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


def to_dynamics_permission(group_type: str, operate: list[str], dynamic_tag: str):
    """
    转换为权限对象
    :param group_type:  分组类型
    :param operate:     操作
    :param dynamic_tag: 标记
    :return: 权限列表
    """
    return [Permission(group=Group[group_type], operate=Operate[o], dynamic_tag=dynamic_tag)
            for o in operate]


def get_user_dynamics_permission(user_id: str):
    """
    获取 应用和数据集权限
    :param user_id: 用户id
    :return: 用户 应用和数据集权限
    """
    member_permission_list = select_list(
        get_file_content(os.path.join(PROJECT_DIR, "apps", "setting", 'sql', 'get_user_permission.sql')),
        [user_id, user_id, user_id])
    result = []
    for member_permission in member_permission_list:
        result += to_dynamics_permission(member_permission.get('type'), member_permission.get('operate'),
                                         str(member_permission.get('id')))
    return result


class User(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    email = models.EmailField(unique=True, null=True, blank=True, verbose_name="邮箱")
    phone = models.CharField(max_length=20, verbose_name="电话", default="")
    nick_name = models.CharField(max_length=150, verbose_name="昵称", default="")
    username = models.CharField(max_length=150, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=150, verbose_name="密码")
    role = models.CharField(max_length=150, verbose_name="角色")
    source = models.CharField(max_length=10, verbose_name="来源", default="LOCAL")
    is_active = models.BooleanField(default=True)
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True, null=True)
    update_time = models.DateTimeField(verbose_name="修改时间", auto_now=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "user"

    def set_password(self, raw_password):
        self.password = password_encrypt(raw_password)
        self._password = raw_password
