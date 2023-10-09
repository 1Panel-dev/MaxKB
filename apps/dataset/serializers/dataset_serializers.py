# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： dataset_serializers.py
    @date：2023/9/21 16:14
    @desc:
"""
import os.path
import uuid
from functools import reduce
from typing import Dict

from django.core import validators
from django.db import transaction, models
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import get_dynamics_model, native_page_search, native_search
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.file_util import get_file_content
from dataset.models.data_set import DataSet, Document, Paragraph
from dataset.serializers.document_serializers import CreateDocumentSerializers
from smartdoc.conf import PROJECT_DIR
from users.models import User

"""
# __exact  精确等于 like ‘aaa’
# __iexact 精确等于 忽略大小写 ilike 'aaa'
# __contains 包含like '%aaa%'
# __icontains 包含 忽略大小写 ilike ‘%aaa%’，但是对于sqlite来说，contains的作用效果等同于icontains。
# __gt  大于
# __gte 大于等于
# __lt 小于
# __lte 小于等于
# __in 存在于一个list范围内
# __startswith 以…开头
# __istartswith 以…开头 忽略大小写
# __endswith 以…结尾
# __iendswith 以…结尾，忽略大小写
# __range 在…范围内
# __year 日期字段的年份
# __month 日期字段的月份
# __day 日期字段的日
# __isnull=True/False
"""


class DataSetSerializers(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = ['id', 'name', 'desc', 'create_time', 'update_time']

    class Query(ApiMixin, serializers.Serializer):
        """
        查询对象
        """
        name = serializers.CharField(required=False,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=20,
                                                                       message="数据集名称在1-20个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="数据集名称在1-20个字符之间")
                                     ])

        desc = serializers.CharField(required=False,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=256,
                                                                       message="数据集名称在1-256个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="数据集名称在1-256个字符之间")
                                     ])

        def get_query_set(self):
            query_set = QuerySet(model=get_dynamics_model(
                {'dataset.name': models.CharField(), 'dataset.desc': models.CharField(),
                 "document_temp.char_length": models.IntegerField()}))
            if "desc" in self.data:
                query_string = {'dataset.desc__contains', self.data.get("desc")}
                query_set = query_set.filter(query_string)
            if "name" in self.data:
                query_string = {'dataset.name__contains', self.data.get("name")}
                query_set = query_set.filter(query_string)
            return query_set

        def page(self, current_page: int, page_size: int):
            return native_page_search(current_page, page_size, self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')),
                                      post_records_handler=lambda r: r)

        def list(self):
            return native_search(self.get_query_set(), select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')))

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='name',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='数据集名称'),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='数据集描述')
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(type=openapi.TYPE_ARRAY,
                                  title="数据集列表", description="数据集列表",
                                  items=DataSetSerializers.Operate.get_response_body_api())

    class Create(ApiMixin, serializers.Serializer):
        """
        创建序列化对象
        """
        name = serializers.CharField(required=True,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=20,
                                                                       message="数据集名称在1-20个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="数据集名称在1-20个字符之间")
                                     ])

        desc = serializers.CharField(required=True,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=256,
                                                                       message="数据集名称在1-256个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="数据集名称在1-256个字符之间")
                                     ])

        documents = CreateDocumentSerializers(required=False, many=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            return True

        @transaction.atomic
        def save(self, user: User):
            dataset_id = uuid.uuid1()
            dataset = DataSet(
                **{'id': dataset_id, 'name': self.data.get("name"), 'desc': self.data.get('desc'), 'user': user})
            document_model_list = []
            paragraph_model_list = []
            if 'documents' in self.data:
                documents = self.data.get('documents')
                for document in documents:
                    document_model = Document(**{'dataset': dataset, 'id': uuid.uuid1(), 'name': document.get('name'),
                                                 'char_length': reduce(lambda x, y: x + y,
                                                                       list(
                                                                           map(lambda p: len(p),
                                                                               document.get("paragraphs"))), 0)})
                    document_model_list.append(document_model)
                    if 'paragraphs' in document:
                        paragraph_model_list += list(map(lambda p: Paragraph(
                            **{'document': document_model, 'id': uuid.uuid1(), 'content': p}),
                                                         document.get('paragraphs')))
            # 插入数据集
            dataset.save()
            # 插入文档
            QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None
            # 插入段落
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            return True

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="数据集名称", description="数据集名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="数据集描述", description="数据集描述"),
                    'documents': openapi.Schema(type=openapi.TYPE_ARRAY, title="文档数据", description="文档数据",
                                                items=CreateDocumentSerializers().get_request_body_api()
                                                )
                }
            )

    class Operate(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True)

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get("id")).exists():
                raise AppApiException(300, "id不存在")

        @transaction.atomic
        def delete(self):
            self.is_valid()
            dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            document_list = QuerySet(Document).filter(dataset=dataset)
            QuerySet(Paragraph).filter(document__in=document_list).delete()
            document_list.delete()
            dataset.delete()
            return True

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid()
            query_string = {'dataset.id', self.data.get("id")}
            query_set = QuerySet(model=get_dynamics_model(
                {'dataset.id': models.UUIDField()})).filter(query_string)
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')), with_search_one=True)

        def edit(self, dataset: Dict):
            """
            修改数据集
            :param dataset: Dict name desc
            :return:
            """
            self.is_valid()
            _dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            if "name" in dataset:
                _dataset.name = dataset.get("name")
            if 'desc' in dataset:
                _dataset.desc = dataset.get("desc")
            _dataset.save()
            return self.one(with_valid=False)

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="数据集名称", description="数据集名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="数据集描述", description="数据集描述")
                }
            )

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'user_id', 'char_length', 'document_count',
                          'update_time', 'create_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="名称",
                                           description="名称", default="测试数据集"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="描述",
                                           description="描述", default="测试数据集描述"),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="所属用户id",
                                              description="所属用户id", default="user_xxxx"),
                    'char_length': openapi.Schema(type=openapi.TYPE_STRING, title="字符数",
                                                  description="字符数", default=10),
                    'document_count': openapi.Schema(type=openapi.TYPE_STRING, title="文档数量",
                                                     description="文档数量", default=1),
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
        def get_request_params_api():
            return [openapi.Parameter(name='id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='数据集id')
                    ]
