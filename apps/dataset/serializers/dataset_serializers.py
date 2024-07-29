# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： dataset_serializers.py
    @date：2023/9/21 16:14
    @desc:
"""
import logging
import os.path
import re
import traceback
import uuid
from functools import reduce
from typing import Dict, List
from urllib.parse import urlparse

from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import transaction, models
from django.db.models import QuerySet
from django.http import HttpResponse
from drf_yasg import openapi
from rest_framework import serializers

from application.models import ApplicationDatasetMapping
from common.config.embedding_config import VectorStore
from common.db.search import get_dynamics_model, native_page_search, native_search
from common.db.sql_execute import select_list
from common.event import ListenerManagement, SyncWebDatasetArgs
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.common import post, flat_map, valid_license
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from common.util.fork import ChildLink, Fork
from common.util.split_model import get_split_model
from dataset.models.data_set import DataSet, Document, Paragraph, Problem, Type, ProblemParagraphMapping, Status
from dataset.serializers.common_serializers import list_paragraph, MetaSerializer, ProblemParagraphManage, \
    get_embedding_model_by_dataset_id
from dataset.serializers.document_serializers import DocumentSerializers, DocumentInstanceSerializer
from embedding.models import SearchMode
from setting.models import AuthOperate
from smartdoc.conf import PROJECT_DIR

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
        fields = ['id', 'name', 'desc', 'meta', 'create_time', 'update_time']

    class Application(ApiMixin, serializers.Serializer):
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("用户id"))

        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("数据集id"))

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
                                     error_messages=ErrMessage.char("知识库名称"),
                                     max_length=64,
                                     min_length=1)

        desc = serializers.CharField(required=False,
                                     error_messages=ErrMessage.char("知识库描述"),
                                     max_length=256,
                                     min_length=1,
                                     )

        user_id = serializers.CharField(required=True)

        def get_query_set(self):
            user_id = self.data.get("user_id")
            query_set_dict = {}
            query_set = QuerySet(model=get_dynamics_model(
                {'temp.name': models.CharField(), 'temp.desc': models.CharField(),
                 "document_temp.char_length": models.IntegerField(), 'temp.create_time': models.DateTimeField()}))
            if "desc" in self.data and self.data.get('desc') is not None:
                query_set = query_set.filter(**{'temp.desc__icontains': self.data.get("desc")})
            if "name" in self.data and self.data.get('name') is not None:
                query_set = query_set.filter(**{'temp.name__icontains': self.data.get("name")})
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
        user_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char("用户id"), )

        class CreateBaseSerializers(ApiMixin, serializers.Serializer):
            """
            创建通用数据集序列化对象
            """
            name = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("知识库名称"),
                                         max_length=64,
                                         min_length=1)

            desc = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("知识库描述"),
                                         max_length=256,
                                         min_length=1)

            embedding_mode_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("向量模型"))

            documents = DocumentInstanceSerializer(required=False, many=True)

            def is_valid(self, *, raise_exception=False):
                super().is_valid(raise_exception=True)
                return True

        class CreateQASerializers(serializers.Serializer):
            """
            创建web站点序列化对象
            """
            name = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("知识库名称"),
                                         max_length=64,
                                         min_length=1)

            desc = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("知识库描述"),
                                         max_length=256,
                                         min_length=1)

            embedding_mode_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("向量模型"))

            file_list = serializers.ListSerializer(required=True,
                                                   error_messages=ErrMessage.list("文件列表"),
                                                   child=serializers.FileField(required=True,
                                                                               error_messages=ErrMessage.file("文件")))

            @staticmethod
            def get_request_params_api():
                return [openapi.Parameter(name='file',
                                          in_=openapi.IN_FORM,
                                          type=openapi.TYPE_ARRAY,
                                          items=openapi.Items(type=openapi.TYPE_FILE),
                                          required=True,
                                          description='上传文件'),
                        openapi.Parameter(name='name',
                                          in_=openapi.IN_FORM,
                                          required=True,
                                          type=openapi.TYPE_STRING, title="知识库名称", description="知识库名称"),
                        openapi.Parameter(name='desc',
                                          in_=openapi.IN_FORM,
                                          required=True,
                                          type=openapi.TYPE_STRING, title="知识库描述", description="知识库描述"),
                        ]

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

        class CreateWebSerializers(serializers.Serializer):
            """
            创建web站点序列化对象
            """
            name = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("知识库名称"),
                                         max_length=64,
                                         min_length=1)

            desc = serializers.CharField(required=True,
                                         error_messages=ErrMessage.char("知识库描述"),
                                         max_length=256,
                                         min_length=1)
            source_url = serializers.CharField(required=True, error_messages=ErrMessage.char("Web 根地址"), )

            embedding_mode_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("向量模型"))

            selector = serializers.CharField(required=False, allow_null=True, allow_blank=True,
                                             error_messages=ErrMessage.char("选择器"))

            def is_valid(self, *, raise_exception=False):
                super().is_valid(raise_exception=True)
                source_url = self.data.get('source_url')
                response = Fork(source_url, []).fork()
                if response.status == 500:
                    raise AppApiException(500, f"url错误,无法解析【{source_url}】")
                return True

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
                    required=['name', 'desc', 'url'],
                    properties={
                        'name': openapi.Schema(type=openapi.TYPE_STRING, title="知识库名称", description="知识库名称"),
                        'desc': openapi.Schema(type=openapi.TYPE_STRING, title="知识库描述", description="知识库描述"),
                        'embedding_mode_id': openapi.Schema(type=openapi.TYPE_STRING, title="向量模型id",
                                                            description="向量模型id"),
                        'source_url': openapi.Schema(type=openapi.TYPE_STRING, title="web站点url",
                                                     description="web站点url"),
                        'selector': openapi.Schema(type=openapi.TYPE_STRING, title="选择器", description="选择器")
                    }
                )

        @staticmethod
        def post_embedding_dataset(document_list, dataset_id):
            model = get_embedding_model_by_dataset_id(dataset_id)
            # 发送向量化事件
            ListenerManagement.embedding_by_dataset_signal.send(dataset_id, embedding_model=model)
            return document_list

        def save_qa(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                self.CreateQASerializers(data=instance).is_valid()
            file_list = instance.get('file_list')
            document_list = flat_map([DocumentSerializers.Create.parse_qa_file(file) for file in file_list])
            dataset_instance = {'name': instance.get('name'), 'desc': instance.get('desc'), 'documents': document_list,
                                'embedding_mode_id': instance.get('embedding_mode_id')}
            return self.save(dataset_instance, with_valid=True)

        @valid_license(model=DataSet, count=50,
                       message='社区版最多支持 50 个知识库，如需拥有更多知识库，请联系我们（https://fit2cloud.com/）。')
        @post(post_function=post_embedding_dataset)
        @transaction.atomic
        def save(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                self.CreateBaseSerializers(data=instance).is_valid()
            dataset_id = uuid.uuid1()
            user_id = self.data.get('user_id')
            if QuerySet(DataSet).filter(user_id=user_id, name=instance.get('name')).exists():
                raise AppApiException(500, "知识库名称重复!")
            dataset = DataSet(
                **{'id': dataset_id, 'name': instance.get("name"), 'desc': instance.get('desc'), 'user_id': user_id,
                   'embedding_mode_id': instance.get('embedding_mode_id')})

            document_model_list = []
            paragraph_model_list = []
            problem_paragraph_object_list = []
            # 插入文档
            for document in instance.get('documents') if 'documents' in instance else []:
                document_paragraph_dict_model = DocumentSerializers.Create.get_document_paragraph_model(dataset_id,
                                                                                                        document)
                document_model_list.append(document_paragraph_dict_model.get('document'))
                for paragraph in document_paragraph_dict_model.get('paragraph_model_list'):
                    paragraph_model_list.append(paragraph)
                for problem_paragraph_object in document_paragraph_dict_model.get('problem_paragraph_object_list'):
                    problem_paragraph_object_list.append(problem_paragraph_object)

            problem_model_list, problem_paragraph_mapping_list = (ProblemParagraphManage(problem_paragraph_object_list,
                                                                                         dataset_id)
                                                                  .to_problem_model_list())
            # 插入知识库
            dataset.save()
            # 插入文档
            QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None
            # 批量插入段落
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # 批量插入问题
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # 批量插入关联问题
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None

            # 响应数据
            return {**DataSetSerializers(dataset).data,
                'document_list': DocumentSerializers.Query(data={'dataset_id': dataset_id}).list(
                    with_valid=True)}, dataset_id

        @staticmethod
        def get_last_url_path(url):
            parsed_url = urlparse(url)
            if parsed_url.path is None or len(parsed_url.path) == 0:
                return url
            else:
                return parsed_url.path.split("/")[-1]

        @staticmethod
        def get_save_handler(dataset_id, selector):
            def handler(child_link: ChildLink, response: Fork.Response):
                if response.status == 200:
                    try:
                        document_name = child_link.tag.text if child_link.tag is not None and len(
                            child_link.tag.text.strip()) > 0 else child_link.url
                        paragraphs = get_split_model('web.md').parse(response.content)
                        DocumentSerializers.Create(data={'dataset_id': dataset_id}).save(
                            {'name': document_name, 'paragraphs': paragraphs,
                             'meta': {'source_url': child_link.url, 'selector': selector},
                             'type': Type.web}, with_valid=True)
                    except Exception as e:
                        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

            return handler

        def save_web(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                self.CreateWebSerializers(data=instance).is_valid(raise_exception=True)
            user_id = self.data.get('user_id')
            if QuerySet(DataSet).filter(user_id=user_id, name=instance.get('name')).exists():
                raise AppApiException(500, "知识库名称重复!")
            dataset_id = uuid.uuid1()
            dataset = DataSet(
                **{'id': dataset_id, 'name': instance.get("name"), 'desc': instance.get('desc'), 'user_id': user_id,
                   'type': Type.web,
                   'meta': {'source_url': instance.get('source_url'), 'selector': instance.get('selector'),
                            'embedding_mode_id': instance.get('embedding_mode_id')}})
            dataset.save()
            ListenerManagement.sync_web_dataset_signal.send(
                SyncWebDatasetArgs(str(dataset_id), instance.get('source_url'), instance.get('selector'),
                                   self.get_save_handler(dataset_id, instance.get('selector'))))
            return {**DataSetSerializers(dataset).data,
                    'document_list': []}

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
                    'embedding_mode_id': openapi.Schema(type=openapi.TYPE_STRING, title='向量模型',
                                                        description='向量模型'),
                    'documents': openapi.Schema(type=openapi.TYPE_ARRAY, title="文档数据", description="文档数据",
                                                items=DocumentSerializers().Create.get_request_body_api()
                                                )
                }
            )

    class Edit(serializers.Serializer):
        name = serializers.CharField(required=False, max_length=64, min_length=1,
                                     error_messages=ErrMessage.char("知识库名称"))
        desc = serializers.CharField(required=False, max_length=256, min_length=1,
                                     error_messages=ErrMessage.char("知识库描述"))
        meta = serializers.DictField(required=False)
        application_id_list = serializers.ListSerializer(required=False, child=serializers.UUIDField(required=True,
                                                                                                     error_messages=ErrMessage.char(
                                                                                                         "应用id")),
                                                         error_messages=ErrMessage.char("应用列表"))

        @staticmethod
        def get_dataset_meta_valid_map():
            dataset_meta_valid_map = {
                Type.base: MetaSerializer.BaseMeta,
                Type.web: MetaSerializer.WebMeta
            }
            return dataset_meta_valid_map

        def is_valid(self, *, dataset: DataSet = None):
            super().is_valid(raise_exception=True)
            if 'meta' in self.data and self.data.get('meta') is not None:
                dataset_meta_valid_map = self.get_dataset_meta_valid_map()
                valid_class = dataset_meta_valid_map.get(dataset.type)
                valid_class(data=self.data.get('meta')).is_valid(raise_exception=True)

    class HitTest(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.char("id"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char("用户id"))
        query_text = serializers.CharField(required=True, error_messages=ErrMessage.char("查询文本"))
        top_number = serializers.IntegerField(required=True, max_value=100, min_value=1,
                                              error_messages=ErrMessage.char("响应Top"))
        similarity = serializers.FloatField(required=True, max_value=2, min_value=0,
                                            error_messages=ErrMessage.char("相似度"))
        search_mode = serializers.CharField(required=True, validators=[
            validators.RegexValidator(regex=re.compile("^embedding|keywords|blend$"),
                                      message="类型只支持register|reset_password", code=500)
        ], error_messages=ErrMessage.char("检索模式"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get("id")).exists():
                raise AppApiException(300, "id不存在")

        def hit_test(self):
            self.is_valid()
            vector = VectorStore.get_embedding_vector()
            exclude_document_id_list = [str(document.id) for document in
                                        QuerySet(Document).filter(
                                            dataset_id=self.data.get('id'),
                                            is_active=False)]
            model = get_embedding_model_by_dataset_id(self.data.get('id'))
            # 向量库检索
            hit_list = vector.hit_test(self.data.get('query_text'), [self.data.get('id')], exclude_document_id_list,
                                       self.data.get('top_number'),
                                       self.data.get('similarity'),
                                       SearchMode(self.data.get('search_mode')),
                                       model)
            hit_dict = reduce(lambda x, y: {**x, **y}, [{hit.get('paragraph_id'): hit} for hit in hit_list], {})
            p_list = list_paragraph([h.get('paragraph_id') for h in hit_list])
            return [{**p, 'similarity': hit_dict.get(p.get('id')).get('similarity'),
                     'comprehensive_score': hit_dict.get(p.get('id')).get('comprehensive_score')} for p in p_list]

    class SyncWeb(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.char(
            "知识库id"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char(
            "用户id"))
        sync_type = serializers.CharField(required=True, error_messages=ErrMessage.char(
            "同步类型"), validators=[
            validators.RegexValidator(regex=re.compile("^replace|complete$"),
                                      message="同步类型只支持:replace|complete", code=500)
        ])

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            first = QuerySet(DataSet).filter(id=self.data.get("id")).first()
            if first is None:
                raise AppApiException(300, "id不存在")
            if first.type != Type.web:
                raise AppApiException(500, "只有web站点类型才支持同步")

        def sync(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            sync_type = self.data.get('sync_type')
            dataset_id = self.data.get('id')
            dataset = QuerySet(DataSet).get(id=dataset_id)
            self.__getattribute__(sync_type + '_sync')(dataset)
            return True

        @staticmethod
        def get_sync_handler(dataset):
            def handler(child_link: ChildLink, response: Fork.Response):
                if response.status == 200:
                    try:
                        document_name = child_link.tag.text if child_link.tag is not None and len(
                            child_link.tag.text.strip()) > 0 else child_link.url
                        paragraphs = get_split_model('web.md').parse(response.content)
                        first = QuerySet(Document).filter(meta__source_url=child_link.url, dataset=dataset).first()
                        if first is not None:
                            # 如果存在,使用文档同步
                            DocumentSerializers.Sync(data={'document_id': first.id}).sync()
                        else:
                            # 插入
                            DocumentSerializers.Create(data={'dataset_id': dataset.id}).save(
                                {'name': document_name, 'paragraphs': paragraphs,
                                 'meta': {'source_url': child_link.url, 'selector': dataset.meta.get('selector')},
                                 'type': Type.web}, with_valid=True)
                    except Exception as e:
                        logging.getLogger("max_kb_error").error(f'{str(e)}:{traceback.format_exc()}')

            return handler

        def replace_sync(self, dataset):
            """
            替换同步
            :return:
            """
            url = dataset.meta.get('source_url')
            selector = dataset.meta.get('selector') if 'selector' in dataset.meta else None
            ListenerManagement.sync_web_dataset_signal.send(
                SyncWebDatasetArgs(str(dataset.id), url, selector,
                                   self.get_sync_handler(dataset)))

        def complete_sync(self, dataset):
            """
            完整同步  删掉当前数据集下所有的文档,再进行同步
            :return:
            """
            # 删除关联问题
            QuerySet(ProblemParagraphMapping).filter(dataset=dataset).delete()
            # 删除文档
            QuerySet(Document).filter(dataset=dataset).delete()
            # 删除段落
            QuerySet(Paragraph).filter(dataset=dataset).delete()
            # 删除向量
            ListenerManagement.delete_embedding_by_dataset_signal.send(self.data.get('id'))
            # 同步
            self.replace_sync(dataset)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id'),
                    openapi.Parameter(name='sync_type',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='同步类型->replace:替换同步,complete:完整同步')
                    ]

    class Operate(ApiMixin, serializers.Serializer):
        id = serializers.CharField(required=True, error_messages=ErrMessage.char(
            "知识库id"))
        user_id = serializers.UUIDField(required=False, error_messages=ErrMessage.char(
            "用户id"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(DataSet).filter(id=self.data.get("id")).exists():
                raise AppApiException(300, "id不存在")

        def export_excel(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            document_list = QuerySet(Document).filter(dataset_id=self.data.get('id'))
            paragraph_list = native_search(QuerySet(Paragraph).filter(dataset_id=self.data.get("id")), get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_paragraph_document_name.sql')))
            problem_mapping_list = native_search(
                QuerySet(ProblemParagraphMapping).filter(dataset_id=self.data.get("id")), get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_problem_mapping.sql')),
                with_table_name=True)
            data_dict, document_dict = DocumentSerializers.Operate.merge_problem(paragraph_list, problem_mapping_list,
                                                                                 document_list)
            workbook = DocumentSerializers.Operate.get_workbook(data_dict, document_dict)
            response = HttpResponse(content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="dataset.xls"'
            workbook.save(response)
            return response

        @staticmethod
        def merge_problem(paragraph_list: List[Dict], problem_mapping_list: List[Dict]):
            result = {}
            document_dict = {}

            for paragraph in paragraph_list:
                problem_list = [problem_mapping.get('content') for problem_mapping in problem_mapping_list if
                                problem_mapping.get('paragraph_id') == paragraph.get('id')]
                document_sheet = result.get(paragraph.get('document_id'))
                d = document_dict.get(paragraph.get('document_name'))
                if d is None:
                    document_dict[paragraph.get('document_name')] = {paragraph.get('document_id')}
                else:
                    d.add(paragraph.get('document_id'))

                if document_sheet is None:
                    result[paragraph.get('document_id')] = [[paragraph.get('title'), paragraph.get('content'),
                                                             '\n'.join(problem_list)]]
                else:
                    document_sheet.append([paragraph.get('title'), paragraph.get('content'), '\n'.join(problem_list)])
            result_document_dict = {}
            for d_name in document_dict:
                for index, d_id in enumerate(document_dict.get(d_name)):
                    result_document_dict[d_id] = d_name if index == 0 else d_name + str(index)
            return result, result_document_dict

        @transaction.atomic
        def delete(self):
            self.is_valid()
            dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            QuerySet(Document).filter(dataset=dataset).delete()
            QuerySet(ProblemParagraphMapping).filter(dataset=dataset).delete()
            QuerySet(Paragraph).filter(dataset=dataset).delete()
            QuerySet(Problem).filter(dataset=dataset).delete()
            dataset.delete()
            ListenerManagement.delete_embedding_by_dataset_signal.send(self.data.get('id'))
            return True

        def re_embedding(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            model = get_embedding_model_by_dataset_id(self.data.get('id'))
            QuerySet(Document).filter(dataset_id=self.data.get('id')).update(**{'status': Status.queue_up})
            QuerySet(Paragraph).filter(dataset_id=self.data.get('id')).update(**{'status': Status.queue_up})
            ListenerManagement.embedding_by_dataset_signal.send(self.data.get('id'), embedding_model=model)

        def list_application(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            return select_list(get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_dataset_application.sql')),
                [self.data.get('user_id') if self.data.get('user_id') == str(dataset.user_id) else None,
                 dataset.user_id, self.data.get('user_id')])

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

        @transaction.atomic
        def edit(self, dataset: Dict, user_id: str):
            """
            修改知识库
            :param user_id: 用户id
            :param dataset: Dict name desc
            :return:
            """
            self.is_valid()
            if QuerySet(DataSet).filter(user_id=user_id, name=dataset.get('name')).exclude(
                    id=self.data.get('id')).exists():
                raise AppApiException(500, "知识库名称重复!")
            _dataset = QuerySet(DataSet).get(id=self.data.get("id"))
            DataSetSerializers.Edit(data=dataset).is_valid(dataset=_dataset)
            if 'embedding_mode_id' in dataset:
                _dataset.embedding_mode_id = dataset.get('embedding_mode_id')
            if "name" in dataset:
                _dataset.name = dataset.get("name")
            if 'desc' in dataset:
                _dataset.desc = dataset.get("desc")
            if 'meta' in dataset:
                _dataset.meta = dataset.get('meta')
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
                    'meta': openapi.Schema(type=openapi.TYPE_OBJECT, title="知识库元数据",
                                           description="知识库元数据->web:{source_url:xxx,selector:'xxx'},base:{}"),
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
