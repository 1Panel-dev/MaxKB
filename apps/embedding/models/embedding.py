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
from dataset.models.data_set import Document, Paragraph, DataSet
from django.contrib.postgres.search import SearchVectorField


class SourceType(models.TextChoices):
    """订单类型"""
    PROBLEM = 0, '问题'
    PARAGRAPH = 1, '段落'
    TITLE = 2, '标题'


class SearchMode(models.TextChoices):
    embedding = 'embedding'
    keywords = 'keywords'
    blend = 'blend'


class Embedding(models.Model):
    id = models.CharField(max_length=128, primary_key=True, verbose_name="主键id")

    source_id = models.CharField(max_length=128, verbose_name="资源id")

    source_type = models.CharField(verbose_name='资源类型', max_length=5, choices=SourceType.choices,
                                   default=SourceType.PROBLEM)

    is_active = models.BooleanField(verbose_name="是否可用", max_length=1, default=True)

    dataset = models.ForeignKey(DataSet, on_delete=models.DO_NOTHING, verbose_name="文档关联", db_constraint=False)

    document = models.ForeignKey(Document, on_delete=models.DO_NOTHING, verbose_name="文档关联", db_constraint=False)

    paragraph = models.ForeignKey(Paragraph, on_delete=models.DO_NOTHING, verbose_name="段落关联", db_constraint=False)

    embedding = VectorField(verbose_name="向量")

    search_vector = SearchVectorField(verbose_name="分词", default="")

    meta = models.JSONField(verbose_name="元数据", default=dict)

    class Meta:
        db_table = "embedding"
