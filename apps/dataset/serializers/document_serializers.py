# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： document_serializers.py
    @date：2023/9/22 13:43
    @desc:
"""
import os
import uuid
from functools import reduce
from typing import List, Dict

from django.core import validators
from django.db import transaction
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import native_search, native_page_search
from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.file_util import get_file_content
from common.util.split_model import SplitModel, get_split_model
from dataset.models.data_set import DataSet, Document, Paragraph, Problem
from dataset.serializers.paragraph_serializers import ParagraphSerializers, ParagraphInstanceSerializer
from smartdoc.conf import PROJECT_DIR


class DocumentInstanceSerializer(ApiMixin, serializers.Serializer):
    name = serializers.CharField(required=True,
                                 validators=[
                                     validators.MaxLengthValidator(limit_value=128,
                                                                   message="文档名称在1-128个字符之间"),
                                     validators.MinLengthValidator(limit_value=1,
                                                                   message="数据集名称在1-128个字符之间")
                                 ])

    paragraphs = ParagraphInstanceSerializer(required=False, many=True)

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'paragraphs'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, title="文档名称", description="文档名称"),
                'paragraphs': openapi.Schema(type=openapi.TYPE_ARRAY, title="段落列表", description="段落列表",
                                             items=ParagraphSerializers.Create.get_request_body_api())
            }
        )


class DocumentSerializers(ApiMixin, serializers.Serializer):
    class Query(ApiMixin, serializers.Serializer):
        # 数据集id
        dataset_id = serializers.UUIDField(required=True)

        name = serializers.CharField(required=False,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=128,
                                                                       message="文档名称在1-128个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="数据集名称在1-128个字符之间")
                                     ])

        def get_query_set(self):
            query_set = QuerySet(model=Document)
            query_set = query_set.filter(**{'dataset_id': self.data.get("dataset_id")})
            if 'name' in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'name__contains': self.data.get('name')})
            return query_set

        def list(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_query_set()
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_document.sql')))

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return native_page_search(current_page, page_size, query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_document.sql')))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='文档名称')]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(type=openapi.TYPE_ARRAY,
                                  title="文档列表", description="文档列表",
                                  items=DocumentSerializers.Operate.get_response_body_api())

    class Operate(ApiMixin, serializers.Serializer):
        document_id = serializers.UUIDField(required=True)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='数据集id'),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='文档id')
                    ]

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            document_id = self.data.get('document_id')
            if not QuerySet(Document).filter(id=document_id).exists():
                raise AppApiException(500, "文档id不存在")

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = QuerySet(model=Document)
            query_set = query_set.filter(**{'id': self.data.get("document_id")})
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_document.sql')), with_search_one=True)

        def edit(self, instance: Dict, with_valid=False):
            if with_valid:
                self.is_valid()
            _document = QuerySet(Document).get(id=self.data.get("document_id"))
            update_keys = ['name', 'is_active']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    _document.__setattr__(update_key, instance.get(update_key))
            _document.save()
            return self.one()

        @transaction.atomic
        def delete(self):
            document_id = self.data.get("document_id")
            QuerySet(model=Document).filter(id=document_id).delete()
            # 删除段落
            QuerySet(model=Paragraph).filter(document_id=document_id).delete()
            # 删除问题
            QuerySet(model=Problem).filter(document_id=document_id).delete()
            # 删除向量库
            ListenerManagement.delete_embedding_by_document_signal.send(document_id)
            return True

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'char_length', 'user_id', 'paragraph_count', 'is_active'
                                                                                     'update_time', 'create_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="名称",
                                           description="名称", default="测试数据集"),
                    'char_length': openapi.Schema(type=openapi.TYPE_INTEGER, title="字符数",
                                                  description="字符数", default=10),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="用户id", description="用户id"),
                    'paragraph_count': openapi.Schema(type=openapi.TYPE_INTEGER, title="文档数量",
                                                      description="文档数量", default=1),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用",
                                                description="是否可用", default=True),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                                  description="修改时间",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                                  description="创建时间",
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="文档名称", description="文档名称"),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用", description="是否可用"),
                }
            )

    class Create(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get('dataset_id')).exists():
                raise AppApiException(10000, "数据集id不存在")
            return True

        def save(self, instance: Dict, with_valid=False, with_embedding=True, **kwargs):
            if with_valid:
                DocumentInstanceSerializer(data=instance).is_valid(raise_exception=True)
                self.is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')

            document_model = Document(
                **{'dataset_id': dataset_id,
                   'id': uuid.uuid1(),
                   'name': instance.get('name'),
                   'char_length': reduce(lambda x, y: x + y,
                                         [len(p.get('content')) for p in instance.get('paragraphs', [])],
                                         0)})
            # 插入文档
            document_model.save()

            for paragraph in instance.get('paragraphs') if 'paragraphs' in instance else []:
                ParagraphSerializers.Create(
                    data={'dataset_id': dataset_id, 'document_id': str(document_model.id)}).save(paragraph,
                                                                                                 with_valid=True,
                                                                                                 with_embedding=False)
            if with_embedding:
                ListenerManagement.embedding_by_document_signal.send(str(document_model.id))
            return DocumentSerializers.Operate(
                data={'dataset_id': dataset_id, 'document_id': str(document_model.id)}).one(
                with_valid=True)

        @staticmethod
        def get_request_body_api():
            return DocumentInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='数据集id')
                    ]

    class Split(ApiMixin, serializers.Serializer):
        file = serializers.ListField(required=True)

        limit = serializers.IntegerField(required=False)

        patterns = serializers.ListField(required=False,
                                         child=serializers.CharField(required=True))

        with_filter = serializers.BooleanField(required=False)

        def is_valid(self, *, raise_exception=True):
            super().is_valid()
            files = self.data.get('file')
            for f in files:
                if f.size > 1024 * 1024 * 10:
                    raise AppApiException(500, "上传文件最大不能超过10m")

        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='file',
                                  in_=openapi.IN_FORM,
                                  type=openapi.TYPE_ARRAY,
                                  items=openapi.Items(type=openapi.TYPE_FILE),
                                  required=True,
                                  description='上传文件'),
                openapi.Parameter(name='limit',
                                  in_=openapi.IN_FORM,
                                  required=False,
                                  type=openapi.TYPE_INTEGER, title="分段长度", description="分段长度"),
                openapi.Parameter(name='patterns',
                                  in_=openapi.IN_FORM,
                                  required=False,
                                  type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING),
                                  title="分段正则列表", description="分段正则列表"),
                openapi.Parameter(name='with_filter',
                                  in_=openapi.IN_FORM,
                                  required=False,
                                  type=openapi.TYPE_BOOLEAN, title="是否清除特殊字符", description="是否清除特殊字符"),
            ]

        def parse(self):
            file_list = self.data.get("file")
            return list(map(lambda f: file_to_paragraph(f, self.data.get("patterns"), self.data.get("with_filter"),
                                                        self.data.get("limit")), file_list))

    class Batch(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True)

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_ARRAY, items=DocumentSerializers.Create.get_request_body_api())

        def batch_save(self, instance_list: List[Dict], with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            DocumentInstanceSerializer(many=True, data=instance_list).is_valid(raise_exception=True)
            create_data = {'dataset_id': self.data.get("dataset_id")}
            return [DocumentSerializers.Create(data=create_data).save(instance,
                                                                      with_valid=True)
                    for instance in instance_list]


def file_to_paragraph(file, pattern_list: List, with_filter, limit: int):
    data = file.read()
    if pattern_list is None or len(pattern_list) > 0:
        split_model = SplitModel(pattern_list, with_filter, limit)
    else:
        split_model = get_split_model(file.name)
    try:
        content = data.decode('utf-8')
    except BaseException as e:
        return {'name': file.name,
                'content': []}
    return {'name': file.name,
            'content': split_model.parse(content)
            }
