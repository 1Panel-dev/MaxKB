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
from typing import Dict

from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import transaction, models
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import get_dynamics_model, native_page_search, native_search
from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.file_util import get_file_content
from dataset.models.data_set import DataSet, Document, Paragraph, Problem
from dataset.serializers.document_serializers import DocumentSerializers, DocumentInstanceSerializer
from setting.models import AuthOperate
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

        user_id = serializers.CharField(required=True)

        def get_query_set(self):
            user_id = self.data.get("user_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model(
                {'temp.name': models.CharField(), 'temp.desc': models.CharField(),
                 "document_temp.char_length": models.IntegerField()}))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp.desc__contains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp.name__contains': self.data.get("name")})

            query_set_dict['default_sql'] = query_set

            query_set_dict['dataset_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'dataset.user_id': models.CharField(),
                 })).filter(
                **{'dataset.user_id': user_id}
            )

            query_set_dict['team_member_permission_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'user_id': models.CharField(),
                 'team_member_permission.operate': ArrayField(verbose_name="权限操作列表",
                                                              base_field=models.CharField(max_length=256,
                                                                                          blank=True,
                                                                                          choices=AuthOperate.choices,
                                                                                          default=AuthOperate.USE)
                                                              )})).filter(
                **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE']})

            return query_set_dict

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
            return DataSetSerializers.Operate.get_response_body_api()

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

        documents = DocumentInstanceSerializer(required=False, many=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            return True

        @transaction.atomic
        def save(self, user: User):
            dataset_id = uuid.uuid1()
            dataset = DataSet(
                **{'id': dataset_id, 'name': self.data.get("name"), 'desc': self.data.get('desc'), 'user': user})
            # 插入数据集
            dataset.save()
            for document in self.data.get('documents') if 'documents' in self.data else []:
                DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(document, with_valid=True,
                                                                                 with_embedding=False)
            ListenerManagement.embedding_by_dataset_signal.send(str(dataset.id))
            return {**DataSetSerializers(dataset).data,
                    'document_list': DocumentSerializers.Query(data={'dataset_id': dataset_id}).list(with_valid=True)}

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'user_id', 'char_length', 'document_count',
                          'update_time', 'create_time', 'document_list'],
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
                                                  ),
                    'document_list': openapi.Schema(type=openapi.TYPE_ARRAY, title="文档列表",
                                                    description="文档列表",
                                                    items=DocumentSerializers.Operate.get_response_body_api())
                }
            )

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="数据集名称", description="数据集名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="数据集描述", description="数据集描述"),
                    'documents': openapi.Schema(type=openapi.TYPE_ARRAY, title="文档数据", description="文档数据",
                                                items=DocumentSerializers().Create.get_request_body_api()
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
            QuerySet(Document).filter(dataset=dataset).delete()
            QuerySet(Paragraph).filter(dataset=dataset).delete()
            QuerySet(Problem).filter(dataset=dataset).delete()
            dataset.delete()
            ListenerManagement.delete_embedding_by_dataset_signal.send(self.data.get('id'))
            return True

        def one(self, user_id, with_valid=True):
            if with_valid:
                self.is_valid()
            query_set_dict = {'default_sql': QuerySet(model=get_dynamics_model(
                {'temp.id': models.UUIDField()})).filter(**{'temp.id': self.data.get("id")}),
                              'dataset_custom_sql': QuerySet(model=get_dynamics_model(
                                  {'dataset.user_id': models.CharField()})).filter(
                                  **{'dataset.user_id': user_id}
                              ), 'team_member_permission_custom_sql': QuerySet(
                    model=get_dynamics_model({'user_id': models.CharField(),
                                              'team_member_permission.operate': ArrayField(
                                                  verbose_name="权限操作列表",
                                                  base_field=models.CharField(max_length=256,
                                                                              blank=True,
                                                                              choices=AuthOperate.choices,
                                                                              default=AuthOperate.USE)
                                              )})).filter(
                    **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE']})}

            return native_search(query_set_dict, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')), with_search_one=True)

        def edit(self, dataset: Dict, user_id: str):
            """
            修改数据集
            :param user_id: 用户id
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
            return self.one(with_valid=False, user_id=user_id)

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
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='数据集id')
                    ]
