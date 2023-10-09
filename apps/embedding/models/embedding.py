# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： embedding.py
    @date：2023/9/21 15:46
    @desc:
"""
from django.db import models

from common.field.vector_field import VectorField
from dataset.models.data_set import DataSet


class SourceType(models.TextChoices):
    """订单类型"""
    PROBLEM = 0, '问题'
    PARAGRAPH = 1, '段落'


class Embedding(models.Model):
    id = models.CharField(max_length=128, primary_key=True, verbose_name="主键id")

    source_id = models.CharField(max_length=128, verbose_name="资源id")

    source_type = models.CharField(verbose_name='资源类型', max_length=1, choices=SourceType.choices,
                                   default=SourceType.PROBLEM)

    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, verbose_name="数据集关联")

    embedding = VectorField(verbose_name="向量")

    class Meta:
        db_table = "embedding"
