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

from celery_once import AlreadyQueued
from django.db import transaction
from django.db.models import QuerySet, Count
from drf_yasg import openapi
from rest_framework import serializers

from common.db.search import page_search
from common.event import ListenerManagement
from common.exception.app_exception import AppApiException
from common.mixins.api_mixin import ApiMixin
from common.util.common import post
from common.util.field_message import ErrMessage
from dataset.models import Paragraph, Problem, Document, ProblemParagraphMapping, DataSet, TaskType, State
from dataset.serializers.common_serializers import update_document_char_length, BatchSerializer, ProblemParagraphObject, \
    ProblemParagraphManage, get_embedding_model_id_by_dataset_id
from dataset.serializers.problem_serializers import ProblemInstanceSerializer, ProblemSerializer, ProblemSerializers
from embedding.models import SourceType
from embedding.task.embedding import embedding_by_problem as embedding_by_problem_task, embedding_by_problem, \
    delete_embedding_by_source, enable_embedding_by_paragraph, disable_embedding_by_paragraph, embedding_by_paragraph, \
    delete_embedding_by_paragraph, delete_embedding_by_paragraph_ids, update_embedding_document_id
from dataset.task import generate_related_by_paragraph_id_list
from django.utils.translation import gettext_lazy as _


class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ['id', 'content', 'is_active', 'document_id', 'title',
                  'create_time', 'update_time']


class ParagraphInstanceSerializer(ApiMixin, serializers.Serializer):
    """
    段落实例对象
    """
    content = serializers.CharField(required=True, error_messages=ErrMessage.char(_('content')),
                                    max_length=102400,
                                    min_length=1,
                                    allow_null=True, allow_blank=True)

    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char(_('section title')),
                                  allow_null=True, allow_blank=True)

    problem_list = ProblemInstanceSerializer(required=False, many=True)

    is_active = serializers.BooleanField(required=False, error_messages=ErrMessage.char(_('Is active')))

    @staticmethod
    def get_request_body_api():
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, max_length=4096, title=_('section content'),
                                          description=_('section content')),

                'title': openapi.Schema(type=openapi.TYPE_STRING, max_length=256, title=_('section title'),
                                        description=_('section title')),

                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Is active'), description=_('Is active')),

                'problem_list': openapi.Schema(type=openapi.TYPE_ARRAY, title=_('problem list'),
                                               description=_('problem list'),
                                               items=ProblemInstanceSerializer.get_request_body_api())
            }
        )


class EditParagraphSerializers(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char(
        _('section title')), allow_null=True, allow_blank=True)
    content = serializers.CharField(required=False, max_length=102400, allow_null=True, allow_blank=True,
                                    error_messages=ErrMessage.char(
                                        _('section title')))
    problem_list = ProblemInstanceSerializer(required=False, many=True)


class ParagraphSerializers(ApiMixin, serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, error_messages=ErrMessage.char(
        _('section title')), allow_null=True, allow_blank=True)
    content = serializers.CharField(required=True, max_length=102400, error_messages=ErrMessage.char(
        _('section title')))

    class Problem(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('dataset id')))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('document id')))

        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('paragraph id')))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, _('Paragraph id does not exist'))

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
        def save(self, instance: Dict, with_valid=True, with_embedding=True, embedding_by_problem=None):
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
                raise AppApiException(500, _('Already associated, please do not associate again'))
            problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid1(),
                                                                problem_id=problem.id,
                                                                document_id=self.data.get('document_id'),
                                                                paragraph_id=self.data.get('paragraph_id'),
                                                                dataset_id=self.data.get('dataset_id'))
            problem_paragraph_mapping.save()
            model_id = get_embedding_model_id_by_dataset_id(self.data.get('dataset_id'))
            if with_embedding:
                embedding_by_problem_task({'text': problem.content,
                                           'is_active': True,
                                           'source_type': SourceType.PROBLEM,
                                           'source_id': problem_paragraph_mapping.id,
                                           'document_id': self.data.get('document_id'),
                                           'paragraph_id': self.data.get('paragraph_id'),
                                           'dataset_id': self.data.get('dataset_id'),
                                           }, model_id)

            return ProblemSerializers.Operate(
                data={'dataset_id': self.data.get('dataset_id'),
                      'problem_id': problem.id}).one(with_valid=True)

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('dataset id')),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('document id')),
                    openapi.Parameter(name='paragraph_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('paragraph id'))]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(type=openapi.TYPE_OBJECT,
                                  required=["content"],
                                  properties={
                                      'content': openapi.Schema(
                                          type=openapi.TYPE_STRING, title=_('content'),)
                                  })

        @staticmethod
        def get_response_body_api():
            return openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['id', 'content', 'hit_num', 'dataset_id', 'create_time', 'update_time'],
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_STRING, title="id",
                                         description="id", default="xx"),
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_('question content'),
                                              description=_('question content'), default=_('question content')),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('hit num'), description=_('hit num'),
                                              default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset id'),
                                                 description=_('dataset id'), default='xxx'),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                                  description=_('update time'),
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                                  description=_('create time'),
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )

    class Association(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('dataset id')))

        problem_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('problem id')))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('document id')))

        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('paragraph id')))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            paragraph_id = self.data.get('paragraph_id')
            problem_id = self.data.get("problem_id")
            if not QuerySet(Paragraph).filter(dataset_id=dataset_id, id=paragraph_id).exists():
                raise AppApiException(500, _('Paragraph does not exist'))
            if not QuerySet(Problem).filter(dataset_id=dataset_id, id=problem_id).exists():
                raise AppApiException(500, _('Problem does not exist'))

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
                model_id = get_embedding_model_id_by_dataset_id(self.data.get('dataset_id'))
                embedding_by_problem({'text': problem.content,
                                      'is_active': True,
                                      'source_type': SourceType.PROBLEM,
                                      'source_id': problem_paragraph_mapping.id,
                                      'document_id': self.data.get('document_id'),
                                      'paragraph_id': self.data.get('paragraph_id'),
                                      'dataset_id': self.data.get('dataset_id'),
                                      }, model_id)

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
            delete_embedding_by_source(problem_paragraph_mapping_id)
            return True

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('dataset id')),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('document id'))
                , openapi.Parameter(name='paragraph_id',
                                    in_=openapi.IN_PATH,
                                    type=openapi.TYPE_STRING,
                                    required=True,
                                    description=_('paragraph id')),
                    openapi.Parameter(name='problem_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('problem id'))
                    ]

    class Batch(serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('dataset id')))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('document id')))

        @transaction.atomic
        def batch_delete(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Paragraph, raise_exception=True)
                self.is_valid(raise_exception=True)
            paragraph_id_list = instance.get("id_list")
            QuerySet(Paragraph).filter(id__in=paragraph_id_list).delete()
            delete_problems_and_mappings(paragraph_id_list)
            update_document_char_length(self.data.get('document_id'))
            # 删除向量库
            delete_embedding_by_paragraph_ids(paragraph_id_list)
            return True

    class Migrate(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('dataset id')))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('document id')))
        target_dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('target dataset id')))
        target_document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('target document id')))
        paragraph_id_list = serializers.ListField(required=True, error_messages=ErrMessage.char(_('paragraph id list')),
                                                  child=serializers.UUIDField(required=True,
                                                                              error_messages=ErrMessage.uuid(_('paragraph id'))))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            document_list = QuerySet(Document).filter(
                id__in=[self.data.get('document_id'), self.data.get('target_document_id')])
            document_id = self.data.get('document_id')
            target_document_id = self.data.get('target_document_id')
            if document_id == target_document_id:
                raise AppApiException(5000, _('The document to be migrated is consistent with the target document'))
            if len([document for document in document_list if str(document.id) == self.data.get('document_id')]) < 1:
                raise AppApiException(5000, _('The document id does not exist [{document_id}]').format(
                    document_id=self.data.get('document_id')))
            if len([document for document in document_list if
                    str(document.id) == self.data.get('target_document_id')]) < 1:
                raise AppApiException(5000, _('The target document id does not exist [{document_id}]').format(
                    document_id=self.data.get('target_document_id')))

        @transaction.atomic
        def migrate(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            dataset_id = self.data.get('dataset_id')
            target_dataset_id = self.data.get('target_dataset_id')
            document_id = self.data.get('document_id')
            target_document_id = self.data.get('target_document_id')
            paragraph_id_list = self.data.get('paragraph_id_list')
            paragraph_list = QuerySet(Paragraph).filter(dataset_id=dataset_id, document_id=document_id,
                                                        id__in=paragraph_id_list)
            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(paragraph__in=paragraph_list)
            # 同数据集迁移
            if target_dataset_id == dataset_id:
                if len(problem_paragraph_mapping_list):
                    problem_paragraph_mapping_list = [
                        self.update_problem_paragraph_mapping(target_document_id,
                                                              problem_paragraph_mapping) for problem_paragraph_mapping
                        in
                        problem_paragraph_mapping_list]
                    # 修改mapping
                    QuerySet(ProblemParagraphMapping).bulk_update(problem_paragraph_mapping_list,
                                                                  ['document_id'])
                update_embedding_document_id([paragraph.id for paragraph in paragraph_list],
                                             target_document_id, target_dataset_id, None)
                # 修改段落信息
                paragraph_list.update(document_id=target_document_id)
            # 不同数据集迁移
            else:
                problem_list = QuerySet(Problem).filter(
                    id__in=[problem_paragraph_mapping.problem_id for problem_paragraph_mapping in
                            problem_paragraph_mapping_list])
                # 目标数据集问题
                target_problem_list = list(
                    QuerySet(Problem).filter(content__in=[problem.content for problem in problem_list],
                                             dataset_id=target_dataset_id))

                target_handle_problem_list = [
                    self.get_target_dataset_problem(target_dataset_id, target_document_id, problem_paragraph_mapping,
                                                    problem_list, target_problem_list) for
                    problem_paragraph_mapping
                    in
                    problem_paragraph_mapping_list]

                create_problem_list = [problem for problem, is_create in target_handle_problem_list if
                                       is_create is not None and is_create]
                # 插入问题
                QuerySet(Problem).bulk_create(create_problem_list)
                # 修改mapping
                QuerySet(ProblemParagraphMapping).bulk_update(problem_paragraph_mapping_list,
                                                              ['problem_id', 'dataset_id', 'document_id'])
                target_dataset = QuerySet(DataSet).filter(id=target_dataset_id).first()
                dataset = QuerySet(DataSet).filter(id=dataset_id).first()
                embedding_model_id = None
                if target_dataset.embedding_mode_id != dataset.embedding_mode_id:
                    embedding_model_id = str(target_dataset.embedding_mode_id)
                pid_list = [paragraph.id for paragraph in paragraph_list]
                # 修改段落信息
                paragraph_list.update(dataset_id=target_dataset_id, document_id=target_document_id)
                # 修改向量段落信息
                update_embedding_document_id(pid_list, target_document_id, target_dataset_id, embedding_model_id)

            update_document_char_length(document_id)
            update_document_char_length(target_document_id)

        @staticmethod
        def update_problem_paragraph_mapping(target_document_id: str, problem_paragraph_mapping):
            problem_paragraph_mapping.document_id = target_document_id
            return problem_paragraph_mapping

        @staticmethod
        def get_target_dataset_problem(target_dataset_id: str,
                                       target_document_id: str,
                                       problem_paragraph_mapping,
                                       source_problem_list,
                                       target_problem_list):
            source_problem_list = [source_problem for source_problem in source_problem_list if
                                   source_problem.id == problem_paragraph_mapping.problem_id]
            problem_paragraph_mapping.dataset_id = target_dataset_id
            problem_paragraph_mapping.document_id = target_document_id
            if len(source_problem_list) > 0:
                problem_content = source_problem_list[-1].content
                problem_list = [problem for problem in target_problem_list if problem.content == problem_content]
                if len(problem_list) > 0:
                    problem = problem_list[-1]
                    problem_paragraph_mapping.problem_id = problem.id
                    return problem, False
                else:
                    problem = Problem(id=uuid.uuid1(), dataset_id=target_dataset_id, content=problem_content)
                    target_problem_list.append(problem)
                    problem_paragraph_mapping.problem_id = problem.id
                    return problem, True
            return None

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(name='dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('document id')),
                    openapi.Parameter(name='document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('document id')),
                    openapi.Parameter(name='target_dataset_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('target dataset id')),
                    openapi.Parameter(name='target_document_id',
                                      in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('target document id')),
                    ]

        @staticmethod
        def get_request_body_api():
            return openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_STRING),
                title=_('paragraph id list'),
                description=_('paragraph id list')
            )

    class Operate(ApiMixin, serializers.Serializer):
        # 段落id
        paragraph_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            _('paragraph id')))
        # 知识库id
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            _('dataset id')))
        # 文档id
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            _('document id')))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, _('Paragraph id does not exist'))

        @staticmethod
        def post_embedding(paragraph, instance, dataset_id):
            if 'is_active' in instance and instance.get('is_active') is not None:
                (enable_embedding_by_paragraph if instance.get(
                    'is_active') else disable_embedding_by_paragraph)(paragraph.get('id'))

            else:
                model_id = get_embedding_model_id_by_dataset_id(dataset_id)
                embedding_by_paragraph(paragraph.get('id'), model_id)
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
                        raise AppApiException(500, _('Problem id does not exist'))
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
            return self.one(), instance, self.data.get('dataset_id')

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
            Paragraph.objects.filter(id=paragraph_id).delete()
            delete_problems_and_mappings([paragraph_id])

            update_document_char_length(self.data.get('document_id'))
            delete_embedding_by_paragraph(paragraph_id)

        @staticmethod
        def get_request_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_response_body_api():
            return ParagraphInstanceSerializer.get_request_body_api()

        @staticmethod
        def get_request_params_api():
            return [openapi.Parameter(type=openapi.TYPE_STRING, in_=openapi.IN_PATH, name='paragraph_id',
                                      description=_('paragraph id'))]

    class Create(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            _('dataset id')))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            _('document id')))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                             dataset_id=self.data.get('dataset_id')).exists():
                raise AppApiException(500, _('The document id is incorrect'))

        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                ParagraphSerializers(data=instance).is_valid(raise_exception=True)
                self.is_valid()
            dataset_id = self.data.get("dataset_id")
            document_id = self.data.get('document_id')
            paragraph_problem_model = self.get_paragraph_problem_model(dataset_id, document_id, instance)
            paragraph = paragraph_problem_model.get('paragraph')
            problem_paragraph_object_list = paragraph_problem_model.get('problem_paragraph_object_list')
            problem_model_list, problem_paragraph_mapping_list = (ProblemParagraphManage(problem_paragraph_object_list,
                                                                                         dataset_id).
                                                                  to_problem_model_list())
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
                model_id = get_embedding_model_id_by_dataset_id(dataset_id)
                embedding_by_paragraph(str(paragraph.id), model_id)
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
            problem_paragraph_object_list = [
                ProblemParagraphObject(dataset_id, document_id, paragraph.id, problem.get('content')) for problem in
                (instance.get('problem_list') if 'problem_list' in instance else [])]

            return {'paragraph': paragraph,
                    'problem_paragraph_object_list': problem_paragraph_object_list}

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
                                      description=_('dataset id')),
                    openapi.Parameter(name='document_id', in_=openapi.IN_PATH,
                                      type=openapi.TYPE_STRING,
                                      required=True,
                                      description=_('document id'))
                    ]

    class Query(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            _('dataset id')))

        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.char(
            _('document id')))

        title = serializers.CharField(required=False, error_messages=ErrMessage.char(
            _('section title')))

        content = serializers.CharField(required=False)

        def get_query_set(self):
            query_set = QuerySet(model=Paragraph)
            query_set = query_set.filter(
                **{'dataset_id': self.data.get('dataset_id'), 'document_id': self.data.get("document_id")})
            if 'title' in self.data:
                query_set = query_set.filter(
                    **{'title__icontains': self.data.get('title')})
            if 'content' in self.data:
                query_set = query_set.filter(**{'content__icontains': self.data.get('content')})
            query_set.order_by('-create_time', 'id')
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
                                      description=_('document id')),
                    openapi.Parameter(name='title',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('title')),
                    openapi.Parameter(name='content',
                                      in_=openapi.IN_QUERY,
                                      type=openapi.TYPE_STRING,
                                      required=False,
                                      description=_('content'))
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
                    'content': openapi.Schema(type=openapi.TYPE_STRING, title=_('content'),
                                              description=_('content'), default=_('content')),
                    'title': openapi.Schema(type=openapi.TYPE_STRING, title=_('title'),
                                            description=_('title'), default="xxx"),
                    'hit_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('hit num'), description=_('hit num'),
                                              default=1),
                    'star_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('Number of likes'),
                                               description=_('Number of likes'), default=1),
                    'trample_num': openapi.Schema(type=openapi.TYPE_INTEGER, title=_('Number of dislikes'),
                                                  description=_('Number of dislikes'), default=1),
                    'dataset_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('dataset id'),
                                                 description=_('dataset id'), default='xxx'),
                    'document_id': openapi.Schema(type=openapi.TYPE_STRING, title=_('document id'),
                                                  description=_('document id'), default='xxx'),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, title=_('Is active'),
                                                description=_('Is active'), default=True),
                    'update_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('update time'),
                                                  description=_('update time'),
                                                  default="1970-01-01 00:00:00"),
                    'create_time': openapi.Schema(type=openapi.TYPE_STRING, title=_('create time'),
                                                  description=_('create time'),
                                                  default="1970-01-01 00:00:00"
                                                  )
                }
            )

    class BatchGenerateRelated(ApiMixin, serializers.Serializer):
        dataset_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('dataset id')))
        document_id = serializers.UUIDField(required=True, error_messages=ErrMessage.uuid(_('document id')))

        def batch_generate_related(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            paragraph_id_list = instance.get("paragraph_id_list")
            model_id = instance.get("model_id")
            prompt = instance.get("prompt")
            document_id = self.data.get('document_id')
            ListenerManagement.update_status(QuerySet(Document).filter(id=document_id),
                                             TaskType.GENERATE_PROBLEM,
                                             State.PENDING)
            ListenerManagement.update_status(QuerySet(Paragraph).filter(id__in=paragraph_id_list),
                                             TaskType.GENERATE_PROBLEM,
                                             State.PENDING)
            ListenerManagement.get_aggregation_document_status(document_id)()
            try:
                generate_related_by_paragraph_id_list.delay(document_id, paragraph_id_list, model_id,
                                                            prompt)
            except AlreadyQueued as e:
                raise AppApiException(500, _('The task is being executed, please do not send it again.'))


def delete_problems_and_mappings(paragraph_ids):
    problem_paragraph_mappings = ProblemParagraphMapping.objects.filter(paragraph_id__in=paragraph_ids)
    problem_ids = set(problem_paragraph_mappings.values_list('problem_id', flat=True))

    if problem_ids:
        problem_paragraph_mappings.delete()
        remaining_problem_counts = ProblemParagraphMapping.objects.filter(problem_id__in=problem_ids).values(
            'problem_id').annotate(count=Count('problem_id'))
        remaining_problem_ids = {pc['problem_id'] for pc in remaining_problem_counts}
        problem_ids_to_delete = problem_ids - remaining_problem_ids
        Problem.objects.filter(id__in=problem_ids_to_delete).delete()
    else:
        problem_paragraph_mappings.delete()
