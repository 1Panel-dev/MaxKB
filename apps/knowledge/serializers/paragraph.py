# coding=utf-8

from typing import Dict

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet, Count
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from common.utils.common import post
from knowledge.models import Paragraph, Problem, Document, ProblemParagraphMapping
from knowledge.serializers.common import ProblemParagraphObject, ProblemParagraphManage, \
    get_embedding_model_id_by_knowledge_id, update_document_char_length
from knowledge.serializers.problem import ProblemInstanceSerializer, ProblemSerializer
from knowledge.task import embedding_by_paragraph, enable_embedding_by_paragraph, disable_embedding_by_paragraph, \
    delete_embedding_by_paragraph


class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ['id', 'content', 'is_active', 'document_id', 'title', 'create_time', 'update_time']


class ParagraphInstanceSerializer(serializers.Serializer):
    """
    段落实例对象
    """
    content = serializers.CharField(required=True, label=_('content'), max_length=102400, min_length=1, allow_null=True,
                                    allow_blank=True)
    title = serializers.CharField(required=False, max_length=256, label=_('section title'), allow_null=True,
                                  allow_blank=True)
    problem_list = ProblemInstanceSerializer(required=False, many=True)
    is_active = serializers.BooleanField(required=False, label=_('Is active'))


class EditParagraphSerializers(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, label=_('section title'), allow_null=True,
                                  allow_blank=True)
    content = serializers.CharField(required=False, max_length=102400, allow_null=True, allow_blank=True,
                                    label=_('section title'))
    problem_list = ProblemInstanceSerializer(required=False, many=True)


class ParagraphSerializers(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, label=_('section title'), allow_null=True,
                                  allow_blank=True)
    content = serializers.CharField(required=True, max_length=102400, label=_('section title'))

    class Operate(serializers.Serializer):
        # 段落id
        paragraph_id = serializers.UUIDField(required=True, label=_('paragraph id'))
        # 知识库id
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        # 文档id
        document_id = serializers.UUIDField(required=True, label=_('document id'))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            if not QuerySet(Paragraph).filter(id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, _('Paragraph id does not exist'))

        @staticmethod
        def post_embedding(paragraph, instance, knowledge_id):
            if 'is_active' in instance and instance.get('is_active') is not None:
                (enable_embedding_by_paragraph if instance.get(
                    'is_active') else disable_embedding_by_paragraph)(paragraph.get('id'))

            else:
                model_id = get_embedding_model_id_by_knowledge_id(knowledge_id)
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
                QuerySet(Problem).bulk_create([
                    Problem(
                        id=uuid.uuid7(),
                        content=p.get('content'),
                        paragraph_id=self.data.get('paragraph_id'),
                        knowledge_id=self.data.get('knowledge_id'),
                        document_id=self.data.get('document_id')
                    ) for p in create_problem_list
                ]) if len(create_problem_list) else None

                # 修改问题集合
                QuerySet(Problem).bulk_update([
                    Problem(
                        id=row.get('id'),
                        content=row.get('content')
                    ) for row in update_problem_list], ['content']
                ) if len(update_problem_list) > 0 else None

            _paragraph.save()
            update_document_char_length(self.data.get('document_id'))
            return self.one(), instance, self.data.get('knowledge_id')

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

    class Create(serializers.Serializer):
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                             knowledge_id=self.data.get('knowledge_id')).exists():
                raise AppApiException(500, _('The document id is incorrect'))

        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                ParagraphSerializers(data=instance).is_valid(raise_exception=True)
                self.is_valid()
            knowledge_id = self.data.get("knowledge_id")
            document_id = self.data.get('document_id')
            paragraph_problem_model = self.get_paragraph_problem_model(knowledge_id, document_id, instance)
            paragraph = paragraph_problem_model.get('paragraph')
            problem_paragraph_object_list = paragraph_problem_model.get('problem_paragraph_object_list')
            problem_model_list, problem_paragraph_mapping_list = (
                ProblemParagraphManage(problem_paragraph_object_list, knowledge_id)
                .to_problem_model_list())
            # 插入段落
            paragraph_problem_model.get('paragraph').save()
            # 插入問題
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # 插入问题关联关系
            QuerySet(ProblemParagraphMapping).bulk_create(
                problem_paragraph_mapping_list
            ) if len(problem_paragraph_mapping_list) > 0 else None
            # 修改长度
            update_document_char_length(document_id)
            if with_embedding:
                model_id = get_embedding_model_id_by_knowledge_id(knowledge_id)
                embedding_by_paragraph(str(paragraph.id), model_id)
            return ParagraphSerializers.Operate(
                data={'paragraph_id': str(paragraph.id), 'knowledge_id': knowledge_id, 'document_id': document_id}
            ).one(with_valid=True)

        @staticmethod
        def get_paragraph_problem_model(knowledge_id: str, document_id: str, instance: Dict):
            paragraph = Paragraph(
                id=uuid.uuid7(),
                document_id=document_id,
                content=instance.get("content"),
                knowledge_id=knowledge_id,
                title=instance.get("title") if 'title' in instance else ''
            )
            problem_paragraph_object_list = [ProblemParagraphObject(
                knowledge_id, document_id, str(paragraph.id), problem.get('content')
            ) for problem in (instance.get('problem_list') if 'problem_list' in instance else [])]

            return {
                'paragraph': paragraph,
                'problem_paragraph_object_list': problem_paragraph_object_list
            }

        @staticmethod
        def or_get(exists_problem_list, content, knowledge_id):
            exists = [row for row in exists_problem_list if row.content == content]
            if len(exists) > 0:
                return exists[0]
            else:
                return Problem(id=uuid.uuid7(), content=content, knowledge_id=knowledge_id)


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
