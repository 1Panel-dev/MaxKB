# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： problem_serializers.py
    @date：2023/10/23 13:55
    @desc:
"""
import os
import uuid
from typing import Dict, List

from django.db import transaction
from django.db.models import QuerySet
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import native_search, native_page_search
from common.event import ListenerManagement, UpdateProblemArgs
from common.mixins.api_mixin import ApiMixin
from common.util.field_message import ErrMessage
from common.util.file_util import get_file_content
from dataset.models import Problem, Paragraph, ProblemParagraphMapping, DataSet
from dataset.serializers.common_serializers import get_embedding_model_by_dataset_id
from smartdoc.conf import PROJECT_DIR


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'content', 'dataset_id',
                  'create_time', 'update_time']


class ProblemInstanceSerializer(ApiMixin, serializers.Serializer):
    id = serializers.CharField(required=False, error_messages=ErrMessage.char("问题id"))

    content = serializers.CharField(required=True, max_length=256, error_messages=ErrMessage.char("问题内容"))

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
    class Create(serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))
        problem_list = serializers.ListField(required=True, error_messages=ErrMessage.list("问题列表"),
                                             child=serializers.CharField(required=True,
                                                                         error_messages=ErrMessage.char("问题")))

        def batch(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_list = self.data.get('problem_list')
            problem_list = list(set(problem_list))
            dataset_id = self.data.get('dataset_id')
            exists_problem_content_list = [problem.content for problem in
                                           QuerySet(Problem).filter(dataset_id=dataset_id,
                                                                    content__in=problem_list)]
            problem_instance_list = [Problem(id=uuid.uuid1(), dataset_id=dataset_id, content=problem_content) for
                                     problem_content in
                                     problem_list if
                                     (not exists_problem_content_list.__contains__(problem_content) if
                                      len(exists_problem_content_list) > 0 else True)]

            QuerySet(Problem).bulk_create(problem_instance_list) if len(problem_instance_list) > 0 else None
            return [ProblemSerializer(problem_instance).data for problem_instance in problem_instance_list]

    class Query(serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))
        content = serializers.CharField(required=False, error_messages=ErrMessage.char("问题"))

        def get_query_set(self):
            query_set = QuerySet(model=Problem)
            query_set = query_set.filter(
                **{'dataset_id': self.data.get('dataset_id')})
            if 'content' in self.data:
                query_set = query_set.filter(**{'content__icontains': self.data.get('content')})
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self):
            query_set = self.get_query_set()
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_problem.sql')))

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return native_page_search(current_page, page_size, query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_problem.sql')))

    class BatchOperate(serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))

        def delete(self, problem_id_list: List, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(
                dataset_id=dataset_id,
                problem_id__in=problem_id_list)
            source_ids = [row.id for row in problem_paragraph_mapping_list]
            problem_paragraph_mapping_list.delete()
            QuerySet(Problem).filter(id__in=problem_id_list).delete()
            ListenerManagement.delete_embedding_by_source_ids_signal.send(source_ids)
            return True

    class Operate(serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("知识库id"))

        problem_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid("问题id"))

        def list_paragraph(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(dataset_id=self.data.get("dataset_id"),
                                                                                 problem_id=self.data.get("problem_id"))
            if problem_paragraph_mapping is None or len(problem_paragraph_mapping) == 0:
                return []
            return native_search(
                QuerySet(Paragraph).filter(id__in=[row.paragraph_id for row in problem_paragraph_mapping]),
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "dataset", 'sql', 'list_paragraph.sql')))

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return ProblemInstanceSerializer(QuerySet(Problem).get(**{'id': self.data.get('problem_id')})).data

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(
                dataset_id=self.data.get('dataset_id'),
                problem_id=self.data.get('problem_id'))
            source_ids = [row.id for row in problem_paragraph_mapping_list]
            problem_paragraph_mapping_list.delete()
            QuerySet(Problem).filter(id=self.data.get('problem_id')).delete()
            ListenerManagement.delete_embedding_by_source_ids_signal.send(source_ids)
            return True

        @transaction.atomic
        def edit(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_id = self.data.get('problem_id')
            dataset_id = self.data.get('dataset_id')
            content = instance.get('content')
            problem = QuerySet(Problem).filter(id=problem_id,
                                               dataset_id=dataset_id).first()
            QuerySet(DataSet).filter(id=dataset_id)
            problem.content = content
            problem.save()
            model = get_embedding_model_by_dataset_id(dataset_id)
            ListenerManagement.update_problem_signal.send(UpdateProblemArgs(problem_id, content, model))
