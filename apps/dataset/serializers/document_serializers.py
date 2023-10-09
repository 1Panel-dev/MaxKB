# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： document_serializers.py
    @date：2023/9/22 13:43
    @desc:
"""
import uuid
from functools import reduce

from django.core import validators
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from dataset.models.data_set import DataSet, Document, Paragraph


class CreateDocumentSerializers(ApiMixin, serializers.Serializer):
    name = serializers.CharField(required=True,
                                 validators=[
                                     validators.MaxLengthValidator(limit_value=128,
                                                                   message="文档名称在1-128个字符之间"),
                                     validators.MinLengthValidator(limit_value=1,
                                                                   message="数据集名称在1-128个字符之间")
                                 ])

    paragraphs = serializers.ListField(required=False,
                                       child=serializers.CharField(required=True,
                                                                   validators=[
                                                                       validators.MaxLengthValidator(limit_value=256,
                                                                                                     message="段落在1-256个字符之间"),
                                                                       validators.MinLengthValidator(limit_value=1,
                                                                                                     message="段落在1-256个字符之间")
                                                                   ]))

    def is_valid(self, *, dataset_id=None, raise_exception=False):
        if not QuerySet(DataSet).filter(id=dataset_id).exists():
            raise AppApiException(10000, "数据集id不存在")
        return super().is_valid(raise_exception=True)

    def save(self, dataset_id: str, **kwargs):
        document_model = Document(
            **{'dataset': DataSet(id=dataset_id),
               'id': uuid.uuid1(),
               'name': self.data.get('name'),
               'char_length': reduce(lambda x, y: x + y, list(map(lambda p: len(p), self.data.get("paragraphs"))), 0)})

        paragraph_model_list = list(map(lambda p: Paragraph(
            **{'document': document_model, 'id': uuid.uuid1(), 'content': p}),
                                        self.data.get('paragraphs')))

        # 插入文档
        document_model.save()
        # 插入段落
        QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
        return True

    def get_request_body_api(self):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'paragraph'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, title="文档名称", description="文档名称"),
                'paragraphs': openapi.Schema(type=openapi.TYPE_ARRAY, title="段落列表", description="段落列表",
                                             items=openapi.Schema(type=openapi.TYPE_STRING, title="段落数据",
                                                                  description="段落数据"))
            }
        )

    def get_request_params_api(self):
        return [openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='数据集id')]
