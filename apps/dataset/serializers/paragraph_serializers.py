# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： paragraph_serializers.py
    @date：2023/10/16 15:51
    @desc:
"""
import uuid
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import page_search
from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.common import post
from common.util.field_message import ErrMessage
from dataset.models import Paragraph, Problem, Document, ProblemParagraphMapping
from dataset.serializers.common_serializers import update_document_char_length
from dataset.serializers.problem_serializers import ProblemInstanceSerializer, ProblemSerializer, ProblemSerializers
from embedding.models import SourceType


class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ['id', 'content', 'is_active', 'document_id', 'title',
                  'create_time', 'update_time']


class ParagraphInstanceSerializer(ApiMixin, serializers.Serializer):
    """
    段落实例对象
    """
    content = serializers.CharField(required=True, error_messages=ErrMessage.char("段落内容"),
                                    max_length=4096,
                                    min_length=1,
                                    allow_null=True, allow_blank=True)

    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char("段落标题"),
                                  allow_null=True, allow_blank=True)

    problem_list = ProblemInstanceSerializer(required=False, many=True)

    is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char("段落是否可用"))

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, max_length=4096, title="分段内容",
                                          description="分段内容"),

                'title': openapi.Schema(type=openapi.TYPE_STRING, max_length=256, title="分段标题",
                                        description="分段标题"),

                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title="是否可用", description="是否可用"),

                'problem_list': openapi.Schema(type=openapi.TYPE_ARRAY, title='问题列表',
                                               description="问题列表",
                                               items=ProblemInstanceSerializer.get_request_body_api())
            }
        )


class EditParagraphSerializers(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char(
        "分段标题"), allow_null=True, allow_blank=True)
    content = serializers.CharField(required=False, max_length=4096, allow_null=True, allow_blank=True,
                                    error_messages=ErrMessage.char(
                                        "分段内容"))
    problem_list = ProblemInstanceSerializer(required=False, many=True)


class ParagraphSerializers(ApiMixin, serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char(
        "分段标题"), allow_null=True, allow_blank=True)
    content = serializers.CharField(required=True, max_length=4096, error_messages=ErrMessage.char(
        "分段内容"))

    class Problem(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("文档id"))

        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("段落id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, "段落id不存在")

        def list(self, with_valid=False):
            """
            获取问题列表
            :param with_valid: 是否校验
            :return: 问题列表
            """
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(dataset_id=self.data.get("dataset_id"),
                                                                                 paragraph_id=self.data.get(
                                                                                     'paragraph_id'))
            return [ProblemSerializer(row).data for row in
                    QuerySet(Problem).filter(id__in=[row.problem_id for row in problem_paragraph_mapping])]

        @transaction.atomic
        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                self.is_valid()
                ProblemInstanceSerializer(data=instance).is_valid(raise_exception=True)
            problem = QuerySet(Problem).filter(dataset_id=self.data.get('dataset_id'),
                                               content=instance.get('content')).first()
            if problem is None:
                problem = Problem(id=uuid.uuid1(), dataset_id=self.data.get('dataset_id'),
                                  content=instance.get('content'))
                problem.save()
            if QuerySet(ProblemParagraphMapping).filter(dataset_id=self.data.get('dataset_id'), problem_id=problem.id,
                                                        paragraph_id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, "已经关联,请勿重复关联")
            problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid1(),
                                                                problem_id=problem.id,
                                                                document_id=self.data.get('document_id'),
                                                                paragraph_id=self.data.get('paragraph_id'),
                                                                dataset_id=self.data.get('dataset_id'))
            problem_paragraph_mapping.save()
            if with_embedding:
                ListenerManagement.embedding_by_problem_signal.send({'text': problem.content,
                                                                     'is_active': True,
                                                                     'source_type': SourceType.PROBLEM,
                                                                     'source_id': problem_paragraph_mapping.id,
                                                                     'document_id': self.data.get('document_id'),
                                                                     'paragraph_id': self.data.get('paragraph_id'),
                                                                     'dataset_id': self.data.get('dataset_id'),
                                                                     })

            return ProblemSerializers.Operate(
                data={'dataset_id': self.data.get('dataset_id'),
                      'problem_id': problem.id}).one(with_valid=True)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id'),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='文档id'),
                    openapi.Parameter(name='paragraph_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='段落id')]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_OBJECT,
                                  required=["content"],
                                  properties={
                                      'content': openapi.Schema(
                                          type=openapi.TYPE_STRING, title="内容")
                                  })

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'dataset_id', 'create_time', 'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="问题内容",
                                              description="问题内容", default='问题内容'),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="命中数量", description="命中数量",
                                              default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="知识库id",
                                                 description="知识库id", default='xxx'),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                                  description="修改时间",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                                  description="创建时间",
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )

    class Association(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))

        problem_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("问题id"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("文档id"))

        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("段落id"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            paragraph_id = self.data.get('paragraph_id')
            problem_id = self.data.get("problem_id")
            if not QuerySet(Paragraph).filter(dataset_id=dataset_id, id=paragraph_id).exists():
                raise AppApiException(500, "段落不存在")
            if not QuerySet(Problem).filter(dataset_id=dataset_id, id=problem_id).exists():
                raise AppApiException(500, "问题不存在")

        def association(self, with_valid=True, with_embedding=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem = QuerySet(Problem).filter(id=self.data.get("problem_id")).first()
            problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid1(),
                                                                document_id=self.data.get('document_id'),
                                                                paragraph_id=self.data.get('paragraph_id'),
                                                                dataset_id=self.data.get('dataset_id'),
                                                                problem_id=problem.id)
            problem_paragraph_mapping.save()
            if with_embedding:
                ListenerManagement.embedding_by_problem_signal.send({'text': problem.content,
                                                                     'is_active': True,
                                                                     'source_type': SourceType.PROBLEM,
                                                                     'source_id': problem_paragraph_mapping.id,
                                                                     'document_id': self.data.get('document_id'),
                                                                     'paragraph_id': self.data.get('paragraph_id'),
                                                                     'dataset_id': self.data.get('dataset_id'),
                                                                     })

        def un_association(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(
                paragraph_id=self.data.get('paragraph_id'),
                dataset_id=self.data.get('dataset_id'),
                problem_id=self.data.get(
                    'problem_id')).first()
            problem_paragraph_mapping_id = problem_paragraph_mapping.id
            problem_paragraph_mapping.delete()
            ListenerManagement.delete_embedding_by_source_signal.send(problem_paragraph_mapping_id)
            return True

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id'),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='文档id')
                , openapi.Parameter(name='paragraph_id',
                                    in_=openapi.IN_PATH,
                                    type=openapi.TYPE_STRING,
                                    required=True,
                                    description='段落id'),
                    openapi.Parameter(name='problem_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='问题id')
                    ]

    class Operate(ApiMixin, serializers.Serializer):
        # 段落id
        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "段落id"))
        # 知识库id
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "知识库id"))
        # 文档id
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "文档id"))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, "段落id不存在")

        @staticmethod
        def post_embedding(paragraph, instance):
            if 'is_active' in instance and instance.get('is_active') is not None:
                s = (ListenerManagement.enable_embedding_by_paragraph_signal if instance.get(
                    'is_active') else ListenerManagement.disable_embedding_by_paragraph_signal)
                s.send(paragraph.get('id'))
            else:
                ListenerManagement.embedding_by_paragraph_signal.send(paragraph.get('id'))
            return paragraph

        @post(post_embedding)
        @transaction.atomic
        def edit(self, instance: Dict):
            self.is_valid()
            EditParagraphSerializers(data=instance).is_valid(raise_exception=True)
            _paragraph = QuerySet(Paragraph).get(id=self.data.get("paragraph_id"))
            update_keys = ['title', 'content', 'is_active']
            for update_key in update_keys:
                if update_key in instance and instance.get(update_key) is not None:
                    _paragraph.__setattr__(update_key, instance.get(update_key))

            if 'problem_list' in instance:
                update_problem_list = list(
                    filter(lambda row: 'id' in row and row.get('id') is not None, instance.get('problem_list')))

                create_problem_list = list(filter(lambda row: row.get('id') is None, instance.get('problem_list')))

                # 问题集合
                problem_list = QuerySet(Problem).filter(paragraph_id=self.data.get("paragraph_id"))

                # 校验前端 携带过来的id
                for update_problem in update_problem_list:
                    if not set([str(row.id) for row in problem_list]).__contains__(update_problem.get('id')):
                        raise AppApiException(500, update_problem.get('id') + '问题id不存在')
                # 对比需要删除的问题
                delete_problem_list = list(filter(
                    lambda row: not [str(update_row.get('id')) for update_row in update_problem_list].__contains__(
                        str(row.id)), problem_list)) if len(update_problem_list) > 0 else []
                # 删除问题
                QuerySet(Problem).filter(id__in=[row.id for row in delete_problem_list]).delete() if len(
                    delete_problem_list) > 0 else None
                # 插入新的问题
                QuerySet(Problem).bulk_create(
                    [Problem(id=uuid.uuid1(), content=p.get('content'), paragraph_id=self.data.get('paragraph_id'),
                             dataset_id=self.data.get('dataset_id'), document_id=self.data.get('document_id')) for
                     p in create_problem_list]) if len(create_problem_list) else None

                # 修改问题集合
                QuerySet(Problem).bulk_update(
                    [Problem(id=row.get('id'), content=row.get('content')) for row in update_problem_list],
                    ['content']) if len(
                    update_problem_list) > 0 else None

            _paragraph.save()
            update_document_char_length(self.data.get('document_id'))
            return self.one(), instance

        def get_problem_list(self):
            ProblemParagraphMapping(ProblemParagraphMapping)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(
                paragraph_id=self.data.get("paragraph_id"))
            if len(problem_paragraph_mapping) > 0:
                return [ProblemSerializer(problem).data for problem in
                        QuerySet(Problem).filter(id__in=[ppm.problem_id for ppm in problem_paragraph_mapping])]
            return []

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            return {**ParagraphSerializer(QuerySet(model=Paragraph).get(id=self.data.get('paragraph_id'))).data,
                    'problem_list': self.get_problem_list()}

        def delete(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            paragraph_id = self.data.get('paragraph_id')
            QuerySet(Paragraph).filter(id=paragraph_id).delete()
            QuerySet(ProblemParagraphMapping).filter(paragraph_id=paragraph_id).delete()
            ListenerManagement.delete_embedding_by_paragraph_signal.send(paragraph_id)

        @staticmethod
        def get_request_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_response_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(type=openapi.TYPE_STRING, in_=openapi.IN_PATH, name='paragraph_id',
                                      description="段落id")]

    class Create(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "知识库id"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "文档id"))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                             dataset_id=self.data.get('dataset_id')).exists():
                raise AppApiException(500, "文档id不正确")

        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                ParagraphSerializers(data=instance).is_valid(raise_exception=True)
                self.is_valid()
            dataset_id = self.data.get("dataset_id")
            document_id = self.data.get('document_id')
            paragraph_problem_model = self.get_paragraph_problem_model(dataset_id, document_id, instance)
            paragraph = paragraph_problem_model.get('paragraph')
            problem_model_list = paragraph_problem_model.get('problem_model_list')
            problem_paragraph_mapping_list = paragraph_problem_model.get('problem_paragraph_mapping_list')
            # 插入段落
            paragraph_problem_model.get('paragraph').save()
            # 插入問題
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # 插入问题关联关系
            QuerySet(ProblemParagraphMapping).bulk_create(problem_paragraph_mapping_list) if len(
                problem_paragraph_mapping_list) > 0 else None
            # 修改长度
            update_document_char_length(document_id)
            if with_embedding:
                ListenerManagement.embedding_by_paragraph_signal.send(str(paragraph.id))
            return ParagraphSerializers.Operate(
                data={'paragraph_id': str(paragraph.id), 'dataset_id': dataset_id, 'document_id': document_id}).one(
                with_valid=True)

        @staticmethod
        def get_paragraph_problem_model(dataset_id: str, document_id: str, instance: Dict):
            paragraph = Paragraph(id=uuid.uuid1(),
                                  document_id=document_id,
                                  content=instance.get("content"),
                                  dataset_id=dataset_id,
                                  title=instance.get("title") if 'title' in instance else '')
            problem_list = instance.get('problem_list')
            exists_problem_list = []
            if 'problem_list' in instance and len(problem_list) > 0:
                exists_problem_list = QuerySet(Problem).filter(dataset_id=dataset_id,
                                                               content__in=[p.get('content') for p in
                                                                            problem_list]).all()

            problem_model_list = [
                ParagraphSerializers.Create.or_get(exists_problem_list, problem.get('content'), dataset_id) for
                problem in (
                    instance.get('problem_list') if 'problem_list' in instance else [])]

            problem_paragraph_mapping_list = [
                ProblemParagraphMapping(id=uuid.uuid1(), document_id=document_id, problem_id=problem_model.id,
                                        paragraph_id=paragraph.id,
                                        dataset_id=dataset_id) for
                problem_model in problem_model_list]
            return {'paragraph': paragraph,
                    'problem_model_list': [problem_model for problem_model in problem_model_list if
                                           not list(exists_problem_list).__contains__(problem_model)],
                    'problem_paragraph_mapping_list': problem_paragraph_mapping_list}

        @staticmethod
        def or_get(exists_problem_list, content, dataset_id):
            exists = [row for row in exists_problem_list if row.content == content]
            if len(exists) > 0:
                return exists[0]
            else:
                return Problem(id=uuid.uuid1(), content=content, dataset_id=dataset_id)

        @staticmethod
        def get_request_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='知识库id'),
                    openapi.Parameter(name='document_id', in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description="文档id")
                    ]

    class Query(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "知识库id"))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            "文档id"))

        title = serializers.CharField(required=False, error_messages=ErrMessage.char(
            "段落标题"))

        content = serializers.CharField(required=False)

        def get_query_set(self):
            query_set = QuerySet(model=Paragraph)
            query_set = query_set.filter(
                **{'dataset_id': self.data.get('dataset_id'), 'document_id': self.data.get("document_id")})
            if 'title' in self.data:
                query_set = query_set.filter(
                    **{'title__contains': self.data.get('title')})
            if 'content' in self.data:
                query_set = query_set.filter(**{'content__contains': self.data.get('content')})
            return query_set

        def list(self):
            return list(map(lambda row: ParagraphSerializer(row).data, self.get_query_set()))

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return page_search(current_page, page_size, query_set, lambda row: ParagraphSerializer(row).data)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='文档id'),
                    openapi.Parameter(name='title',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='标题'),
                    openapi.Parameter(name='content',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description='内容')
                    ]

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'star_num', 'trample_num', 'is_active', 'dataset_id',
                          'document_id', 'title',
                          'create_time', 'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="段落内容",
                                              description="段落内容", default='段落内容'),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, title="标题",
                                            description="标题", default="xxx的描述"),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="命中数量", description="命中数量",
                                              default=1),
                    'star_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="点赞数量",
                                               description="点赞数量", default=1),
                    'trample_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="点踩数量",
                                                  description="点踩数", default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title="知识库id",
                                                 description="知识库id", default='xxx'),
                    'document_id': openapi.Schema(type=openapi.TYPE_STRING, title="文档id",
                                                  description="文档id", default='xxx'),
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
