# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： problem_serializers.py
    @date：2023/10/23 13:55
    @desc:
"""
import uuid
from typing import Dict

from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from dataset.models import Problem, Paragraph
from embedding.models import SourceType
from embedding.vector.pg_vector import PGVector


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'content', 'hit_num', 'star_num', 'trample_num', 'dataset_id', 'document_id',
                  'create_time', 'update_time']


class ProblemInstanceSerializer(ApiMixin, serializers.Serializer):
    id = serializers.CharField(required=False)

    content = serializers.CharField(required=True)

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(type=openapi.TYPE_OBJECT,
                              required=["content"],
                              properties={
                                  'id': openapi.Schema(
                                      type=openapi.TYPE_STRING,
                                      title="问题id,修改的时候传递,创建的时候不传"),
                                  'content': openapi.Schema(
                                      type=openapi.TYPE_STRING, title="内容")
                              })


class ProblemSerializers(ApiMixin, serializers.Serializer):
    class Create(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True)

        document_id = serializers.UUIDField(required=True)

        paragraph_id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id'),
                                              document_id=self.data.get('document_id'),
                                              dataset_id=self.data.get('dataset_id')).exists():
                raise AppApiException(500, "段落id不正确")

        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                self.is_valid()
                ProblemInstanceSerializer(data=instance).is_valid(raise_exception=True)
            problem = Problem(id=uuid.uuid1(), paragraph_id=self.data.get('paragraph_id'),
                              document_id=self.data.get('document_id'), dataset_id=self.data.get('dataset_id'),
                              content=instance.get('content'))
            problem.save()
            if with_embedding:
                ListenerManagement.embedding_by_problem_signal.send({'text': problem.content,
                                                                     'is_active': True,
                                                                     'source_type': SourceType.PROBLEM,
                                                                     'source_id': problem.id,
                                                                     'document_id': self.data.get('document_id'),
                                                                     'paragraph_id': self.data.get('paragraph_id'),
                                                                     'dataset_id': self.data.get('dataset_id'),
                                                                     'star_num': 0,
                                                                     'trample_num': 0})

            return ProblemSerializers.Operate(
                data={'dataset_id': self.data.get('dataset_id'), 'document_id': self.data.get('document_id'),
                      'paragraph_id': self.data.get('paragraph_id'), 'problem_id': problem.id}).one(with_valid=True)

        @staticmethod
        def get_request_body_api():
            return ProblemInstanceSerializer.get_request_body_api()

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
                                      description='文档id'),
                    openapi.Parameter(name='paragraph_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description='段落id')]

    class Query(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True)

        document_id = serializers.UUIDField(required=True)

        paragraph_id = serializers.UUIDField(required=True)

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, "段落id不存在")

        def get_query_set(self):
            dataset_id = self.data.get('dataset_id')
            document_id = self.data.get('document_id')
            paragraph_id = self.data.get("paragraph_id")
            return QuerySet(Problem).filter(
                **{'paragraph_id': paragraph_id, 'dataset_id': dataset_id, 'document_id': document_id})

        def list(self, with_valid=False):
            """
            获取问题列表
            :param with_valid: 是否校验
            :return: 问题列表
            """
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = self.get_query_set()
            return [ProblemSerializer(p).data for p in query_set]

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
                , openapi.Parameter(name='paragraph_id',
                                    in_=openapi.IN_PATH,
                                    type=openapi.TYPE_STRING,
                                    required=True,
                                    description='段落id')]

    class Operate(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True)

        document_id = serializers.UUIDField(required=True)

        paragraph_id = serializers.UUIDField(required=True)

        problem_id = serializers.UUIDField(required=True)

        def delete(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            QuerySet(Problem).filter(**{'id': self.data.get('problem_id')}).delete()
            PGVector().delete_by_source_id(self.data.get('problem_id'), SourceType.PROBLEM)
            ListenerManagement.delete_embedding_by_source_signal.send(self.data.get('problem_id'))
            return True

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            return ProblemInstanceSerializer(QuerySet(Problem).get(**{'id': self.data.get('problem_id')})).data

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

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'star_num', 'trample_num', 'dataset_id',
                          'document_id',
                          'create_time', 'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title="问题内容",
                                              description="问题内容", default='问题内容'),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="命中数量", description="命中数量",
                                              default=1),
                    'star_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="点赞数量",
                                               description="点赞数量", default=1),
                    'trample_num': openapi.Schema(type=openapi.TYPE_INTEGER, title="点踩数量",
                                                  description="点踩数", default=1),
                    'document_id': openapi.Schema(type=openapi.TYPE_STRING, title="文档id",
                                                  description="文档id", default='xxx'),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title="修改时间",
                                                  description="修改时间",
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title="创建时间",
                                                  description="创建时间",
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )
