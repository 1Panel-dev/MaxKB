# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： team_management.py
    @date：2023/9/25 15:04
    @desc:
"""
import uuid

from django.contrib.postgres.fields import ArrayField
from django.db import models

from common.constants.permission_constants import Group, Operate
from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class AuthTargetType(models.TextChoices):
    """授权目标"""
    DATASET = Group.DATASET.value, '数据集'
    APPLICATION = Group.APPLICATION.value, '应用'


class AuthOperate(models.TextChoices):
    """授权权限"""
    MANAGE = Operate.MANAGE.value, '管理'

    USE = Operate.USE.value, "使用"


class Team(AppModelMixin):
    """
    团队表
    """
    user = models.OneToOneField(User, primary_key=True, on_delete=models.DO_NOTHING, verbose_name="团队所有者")

    name = models.CharField(max_length=128, verbose_name="团队名称")

    class Meta:
        db_table = "team"


class TeamMember(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    team = models.ForeignKey(Team, on_delete=models.DO_NOTHING, verbose_name="团队id")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="成员用户id")

    class Meta:
        db_table = "team_member"


class TeamMemberPermission(AppModelMixin):
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    """
    团队成员权限
    """
    member = models.ForeignKey(TeamMember, on_delete=models.DO_NOTHING, verbose_name="团队成员")

    auth_target_type = models.CharField(verbose_name='授权目标', max_length=128, choices=AuthTargetType.choices,
                                        default=AuthTargetType.DATASET)

    target = models.UUIDField(max_length=128, verbose_name="数据集/应用id")

    operate = ArrayField(verbose_name="权限操作列表",
                         base_field=models.CharField(max_length=256,
                                                     blank=True,
                                                     choices=AuthOperate.choices,
                                                     default=AuthOperate.USE),
                         )

    class Meta:
        db_table = "team_member_permission"
