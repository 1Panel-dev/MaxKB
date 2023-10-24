# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： data_set.py
    @date：2023/9/21 9:35
    @desc: 数据集
"""
import uuid

from django.db import models

from common.mixins.app_model_mixin import AppModelMixin
from users.models import User


class Status(models.TextChoices):
    """订单类型"""
    embedding = 0, '导入中'
    success = 1, '已完成'
    error = 2, '导入失败'


class DataSet(AppModelMixin):
    """
    数据集表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    name = models.CharField(max_length=150, verbose_name="数据集名称")
    desc = models.CharField(max_length=256, verbose_name="数据库描述")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="所属用户")

    class Meta:
        db_table = "dataset"


class Document(AppModelMixin):
    """
    文档表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=150, verbose_name="文档名称")
    char_length = models.IntegerField(verbose_name="文档字符数 冗余字段")
    status = models.CharField(verbose_name='状态', max_length=1, choices=Status.choices,
                              default=Status.embedding)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "document"


class Paragraph(AppModelMixin):
    """
    段落表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING)
    content = models.CharField(max_length=1024, verbose_name="段落内容")
    title = models.CharField(max_length=256, verbose_name="标题", default="")
    hit_num = models.IntegerField(verbose_name="命中数量", default=0)
    star_num = models.IntegerField(verbose_name="点赞数", default=0)
    trample_num = models.IntegerField(verbose_name="点踩数", default=0)
    status = models.CharField(verbose_name='状态', max_length=1, choices=Status.choices,
                              default=Status.embedding)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "paragraph"


class Problem(AppModelMixin):
    """
    问题表
    """
    id = models.UUIDField(primary_key=True, max_length=128, default=uuid.uuid1, editable=False, verbose_name="主键id")
    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, db_constraint=False)
    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, db_constraint=False)
    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, db_constraint=False)
    content = models.CharField(max_length=256, verbose_name="问题内容")
    hit_num = models.IntegerField(verbose_name="命中数量", default=0)
    star_num = models.IntegerField(verbose_name="点赞数", default=0)
    trample_num = models.IntegerField(verbose_name="点踩数", default=0)

    class Meta:
        db_table = "problem"
