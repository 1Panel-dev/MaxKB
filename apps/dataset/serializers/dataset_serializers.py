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
from itertools import groupby
from typing import Dict

from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import transaction, models
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from application.models import ApplicationDatasetMapping
from common.config.embedding_config import VectorStore, EmbeddingModel
from common.db.search import get_dynamics_model, native_page_search, native_search
from common.db.sql_execute import select_list
from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.common import post
from common.util.file_util import get_file_content
from dataset.models.data_set import DataSet, Document, Paragraph, Problem
from dataset.serializers.common_serializers import list_paragraph
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

    class Application(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True)

        dataset_id = serializers.UUIDField(required=True)

        @staticmethod
        def get_request_params_api():
            return [
                openapi.Parameter(name='dataset_id',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_STRING,
                                  required=True,
                                  description='知识库id')
            ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'name', 'desc', 'model_id', 'multiple_rounds_dialogue', 'user_id', 'status',
                          'create_time',
                          'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="", description="主键id"),
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="应用名称", description="应用名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="应用描述", description="应用描述"),
                    'model_id': openapi.Schema(type=openapi.TYPE_STRING, title="模型id", description="模型id"),
                    "multiple_rounds_dialogue": openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否开启多轮对话",
                                                               description="是否开启多轮对话"),
                    'prologue': openapi.Schema(type=openapi.TYPE_STRING, title="开场白", description="开场白"),
                    'example': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING),
                                              title="示例列表", description="示例列表"),
                    'user_id': openapi.Schema(type=openapi.TYPE_STRING, title="所属用户", description="所属用户"),

                    'status': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否发布", description='是否发布'),

                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间", description='创建时间'),

                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间", description='修改时间')
                }
            )

    class Query(ApiMixin, serializers.Serializer):
        """
        查询对象
        """
        name = serializers.CharField(required=False,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=20,
                                                                       message="知识库名称在1-20个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="知识库名称在1-20个字符之间")
                                     ])

        desc = serializers.CharField(required=False,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=256,
                                                                       message="知识库名称在1-256个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="知识库名称在1-256个字符之间")
                                     ])

        user_id = serializers.CharField(required=True)

        def get_query_set(self):
            user_id = self.data.get("user_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model(
                {'temp.name': models.CharField(), 'temp.desc': models.CharField(),
                 "document_temp.char_length": models.IntegerField(), 'temp.create_time': models.DateTimeField()}))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp.desc__contains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp.name__contains': self.data.get("name")})
            query_set = query_set.order_by("-temp.create_time")
            query_set_dict['default_sql'] = query_set

            query_set_dict['dataset_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'dataset.user_id': models.CharField(),
                 })).filter(
                **{'dataset.user_id': user_id}
            )

            query_set_dict['team_member_permission_custom_sql'] = QuerySet(model=get_dynamics_model(
                {'user_id': models.CharField(),
                 'team_member_permission.auth_target_type': models.CharField(),
                 'team_member_permission.operate': ArrayField(verbose_name="权限操作列表",
                                                              base_field=models.CharField(max_length=256,
                                                                                          blank=True,
                                                                                          choices=AuthOperate.choices,
                                                                                          default=AuthOperate.USE)
                                                              )})).filter(
                **{'user_id': user_id, 'team_member_permission.operate__contains': ['USE'],
                   'team_member_permission.auth_target_type': 'DATASET'})

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
                                      description='知识库名称'),
                    openapi.Parameter(name='desc',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='知识库描述')
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
                                                                       message="知识库名称在1-20个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="知识库名称在1-20个字符之间")
                                     ])

        desc = serializers.CharField(required=True,
                                     validators=[
                                         validators.MaxLengthValidator(limit_value=256,
                                                                       message="知识库名称在1-256个字符之间"),
                                         validators.MinLengthValidator(limit_value=1,
                                                                       message="知识库名称在1-256个字符之间")
                                     ])

        documents = DocumentInstanceSerializer(required=False, many=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            return True

        @staticmethod
        def post_embedding_dataset(document_list, dataset_id):
            # 发送向量化事件
            ListenerManagement.embedding_by_dataset_signal.send(dataset_id)
            return document_list

        @post(post_function=post_embedding_dataset)
        @transaction.atomic
        def save(self, user: User):
            dataset_id = uuid.uuid1()
            dataset = DataSet(
                **{'id': dataset_id, 'name': self.data.get("name"), 'desc': self.data.get('desc'), 'user': user})

            document_model_list = []
            paragraph_model_list = []
            problem_model_list = []
            # 插入文档
            for document in self.data.get('documents') if 'documents' in self.data else []:
                document_paragraph_dict_model = DocumentSerializers.Create.get_document_paragraph_model(dataset_id,
                                                                                                        document)
                document_model_list.append(document_paragraph_dict_model.get('document'))
                for paragraph in document_paragraph_dict_model.get('paragraph_model_list'):
                    paragraph_model_list.append(paragraph)
                for problem in document_paragraph_dict_model.get('problem_model_list'):
                    problem_model_list.append(problem)

            # 插入知识库
            dataset.save()
            # 插入文档
            QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None
            # 批量插入段落
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # 批量插入问题
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None

            # 响应数据
            return {**DataSetSerializers(dataset).data,
                'document_list': DocumentSerializers.Query(data={'dataset_id': dataset_id}).list(
                    with_valid=True)}, dataset_id

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
                                           description="名称", default="测试知识库"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="描述",
                                           description="描述", default="测试知识库描述"),
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
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="知识库名称", description="知识库名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="知识库描述", description="知识库描述"),
                    'documents': openapi.Schema(type=openapi.TYPE_ARRAY, title="文档数据", description="文档数据",
                                                items=DocumentSerializers().Create.get_request_body_api()
                                                )
                }
            )

    class Edit(serializers.Serializer):

        name = serializers.CharField(required=False)
        desc = serializers.CharField(required=False)
        application_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True))

    class HitTest(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True)
        user_id = serializers.UUIDField(required=False)
        query_text = serializers.CharField(required=True)
        top_number = serializers.IntegerField(required=True, max_value=10, min_value=1)
        similarity = serializers.FloatField(required=True, max_value=1, min_value=0)

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get("id")).exists():
                raise AppApiException(300, "id不存在")

        def hit_test(self):
            self.is_valid()
            vector = VectorStore.get_embedding_vector()
            # 向量库检索
            hit_list = vector.hit_test(self.data.get('query_text'), [self.data.get('id')], self.data.get('top_number'),
                                       self.data.get('similarity'),
                                       EmbeddingModel.get_embedding_model())
            hit_dict = reduce(lambda x, y: {**x, **y}, [{hit.get('paragraph_id'): hit} for hit in hit_list], {})
            p_list = list_paragraph([h.get('paragraph_id') for h in hit_list])
            return [{**p, 'similarity': hit_dict.get(p.get('id')).get('similarity'),
                     'comprehensive_score': hit_dict.get(p.get('id')).get('comprehensive_score')} for p in p_list]

    class Operate(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True)
        user_id = serializers.UUIDField(required=False)

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

        def list_application(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            return select_list(get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset_application.sql')),
                [self.data.get('user_id'), dataset.user_id, self.data.get('user_id')])

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
            all_application_list = [str(adm.get('id')) for adm in self.list_application(with_valid=False)]
            return {**native_search(query_set_dict, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset.sql')), with_search_one=True),
                'application_id_list': list(
                    filter(lambda application_id: all_application_list.__contains__(application_id),
                           [str(application_dataset_mapping.application_id) for
                            application_dataset_mapping in
                            QuerySet(ApplicationDatasetMapping).filter(
                                dataset_id=self.data.get('id'))]))}

        def edit(self, dataset: Dict, user_id: str):
            """
            修改知识库
            :param user_id: 用户id
            :param dataset: Dict name desc
            :return:
            """
            self.is_valid()
            DataSetSerializers.Edit(data=dataset).is_valid(raise_exception=True)
            _dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            if "name" in dataset:
                _dataset.name = dataset.get("name")
            if 'desc' in dataset:
                _dataset.desc = dataset.get("desc")
            if 'application_id_list' in dataset and dataset.get('application_id_list') is not None:
                application_id_list = dataset.get('application_id_list')
                # 当前用户可修改关联的知识库列表
                application_dataset_id_list = [str(dataset_dict.get('id')) for dataset_dict in
                                               self.list_application(with_valid=False)]
                for dataset_id in application_id_list:
                    if not application_dataset_id_list.__contains__(dataset_id):
                        raise AppApiException(500, f"未知的应用id${dataset_id},无法关联")

                # 删除已经关联的id
                QuerySet(ApplicationDatasetMapping).filter(application_id__in=application_dataset_id_list,
                                                           dataset_id=self.data.get("id")).delete()
                # 插入
                QuerySet(ApplicationDatasetMapping).bulk_create(
                    [ApplicationDatasetMapping(application_id=application_id, dataset_id=self.data.get('id')) for
                     application_id in
                     application_id_list]) if len(application_id_list) > 0 else None
                [ApplicationDatasetMapping(application_id=application_id, dataset_id=self.data.get('id')) for
                 application_id in application_id_list]

            _dataset.save()
            return self.one(with_valid=False, user_id=user_id)

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['name', 'desc'],
                properties={
                    'name': openapi.Schema(type=openapi.TYPE_STRING, title="知识库名称", description="知识库名称"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="知识库描述", description="知识库描述"),
                    'application_id_list': openapi.Schema(type=openapi.TYPE_ARRAY, title="应用id列表",
                                                          description="应用id列表",
                                                          items=openapi.Schema(type=openapi.TYPE_STRING))
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
                                           description="名称", default="测试知识库"),
                    'desc': openapi.Schema(type=openapi.TYPE_STRING, title="描述",
                                           description="描述", default="测试知识库描述"),
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
                                      description='知识库id')
                    ]
