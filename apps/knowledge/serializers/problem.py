import os
from functools import reduce
from typing import Dict, List

import uuid_utils.compat as uuid
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import native_search, native_page_search
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from knowledge.models import Problem, ProblemParagraphMapping, Paragraph, Knowledge, SourceType
from knowledge.serializers.common import get_embedding_model_id_by_knowledge_id
from knowledge.task.embedding import delete_embedding_by_source_ids, update_problem_embedding, embedding_by_data_list
from maxkb.const import PROJECT_DIR


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'content', 'knowledge_id', 'create_time', 'update_time']


class ProblemInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, label=_('problem id'))
    content = serializers.CharField(required=True, max_length=256, label=_('content'))


class ProblemEditSerializer(serializers.Serializer):
    content = serializers.CharField(required=True, max_length=256, label=_('content'))


class ProblemMappingSerializer(serializers.Serializer):
    paragraph_id = serializers.UUIDField(required=True, label=_('paragraph id'))
    document_id = serializers.UUIDField(required=True, label=_('document id'))


class ProblemBatchSerializer(serializers.Serializer):
    problem_list = serializers.ListField(required=True, label=_('problem list'),
                                         child=serializers.CharField(required=True, max_length=256, label=_('problem')))


class ProblemBatchDeleteSerializer(serializers.Serializer):
    problem_id_list = serializers.ListField(required=True, label=_('problem id list'),
                                            child=serializers.UUIDField(required=True, label=_('problem id')))


class AssociationParagraph(serializers.Serializer):
    paragraph_id = serializers.UUIDField(required=True, label=_('paragraph id'))
    document_id = serializers.UUIDField(required=True, label=_('document id'))


class BatchAssociation(serializers.Serializer):
    problem_id_list = serializers.ListField(required=True, label=_('problem id list'),
                                            child=serializers.UUIDField(required=True, label=_('problem id')))
    paragraph_list = AssociationParagraph(many=True)


class ProblemSerializers(serializers.Serializer):
    class BatchOperate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        def delete(self, problem_id_list: List, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            knowledge_id = self.data.get('knowledge_id')
            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(
                knowledge_id=knowledge_id,
                problem_id__in=problem_id_list)
            source_ids = [row.id for row in problem_paragraph_mapping_list]
            problem_paragraph_mapping_list.delete()
            QuerySet(Problem).filter(id__in=problem_id_list).delete()
            delete_embedding_by_source_ids(source_ids)
            return True

        def association(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                BatchAssociation(data=instance).is_valid(raise_exception=True)
            knowledge_id = self.data.get('knowledge_id')
            paragraph_list = instance.get('paragraph_list')
            problem_id_list = instance.get('problem_id_list')
            problem_list = QuerySet(Problem).filter(id__in=problem_id_list)

            exits_problem_paragraph_mapping = QuerySet(
                ProblemParagraphMapping
            ).filter(problem_id__in=problem_id_list, paragraph_id__in=[p.get('paragraph_id') for p in paragraph_list])

            problem_paragraph_mapping_list = [
                (problem_paragraph_mapping, problem) for problem_paragraph_mapping, problem in
                reduce(
                    lambda x, y: [*x, *y],
                    [
                        [
                            to_problem_paragraph_mapping(
                                problem, paragraph.get('document_id'),
                                paragraph.get('paragraph_id'),
                                knowledge_id
                            ) for paragraph in paragraph_list
                        ] for problem in problem_list
                    ],
                    []
                ) if not is_exits(exits_problem_paragraph_mapping, problem_paragraph_mapping)
            ]

            QuerySet(ProblemParagraphMapping).bulk_create(
                [problem_paragraph_mapping for problem_paragraph_mapping, problem in problem_paragraph_mapping_list]
            )

            data_list = [
                {
                    'text': problem.content,
                    'is_active': True,
                    'source_type': SourceType.PROBLEM,
                    'source_id': str(problem_paragraph_mapping.id),
                    'document_id': str(problem_paragraph_mapping.document_id),
                    'paragraph_id': str(problem_paragraph_mapping.paragraph_id),
                    'knowledge_id': knowledge_id,
                } for problem_paragraph_mapping, problem in problem_paragraph_mapping_list
            ]
            model_id = get_embedding_model_id_by_knowledge_id(self.data.get('knowledge_id'))
            embedding_by_data_list(data_list, model_id=model_id)

    class Operate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        problem_id = serializers.UUIDField(required=True, label=_('problem id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        def list_paragraph(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(
                knowledge_id=self.data.get("knowledge_id"),
                problem_id=self.data.get("problem_id")
            )
            if problem_paragraph_mapping is None or len(problem_paragraph_mapping) == 0:
                return []
            return native_search(
                QuerySet(Paragraph).filter(id__in=[row.paragraph_id for row in problem_paragraph_mapping]),
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_paragraph.sql')))

        def one(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            return ProblemInstanceSerializer(QuerySet(Problem).get(**{'id': self.data.get('problem_id')})).data

        @transaction.atomic
        def delete(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(
                knowledge_id=self.data.get('knowledge_id'),
                problem_id=self.data.get('problem_id'))
            source_ids = [row.id for row in problem_paragraph_mapping_list]
            problem_paragraph_mapping_list.delete()
            QuerySet(Problem).filter(id=self.data.get('problem_id')).delete()
            delete_embedding_by_source_ids(source_ids)
            return True

        @transaction.atomic
        def edit(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_id = self.data.get('problem_id')
            knowledge_id = self.data.get('knowledge_id')
            content = instance.get('content')
            problem = QuerySet(Problem).filter(id=problem_id, knowledge_id=knowledge_id).first()
            QuerySet(Knowledge).filter(id=knowledge_id)
            problem.content = content
            problem.save()
            model_id = get_embedding_model_id_by_knowledge_id(knowledge_id)
            update_problem_embedding(problem_id, content, model_id)

    class Create(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        def batch(self, problem_list, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                ProblemBatchSerializer(data={'problem_list': problem_list}).is_valid(raise_exception=True)
            problem_list = list(set(problem_list))
            knowledge_id = self.data.get('knowledge_id')
            exists_problem_content_list = [
                problem.content for problem in QuerySet(
                    Problem
                ).filter(knowledge_id=knowledge_id, content__in=problem_list)
            ]
            problem_instance_list = [
                Problem(
                    id=uuid.uuid7(), knowledge_id=knowledge_id, content=problem_content
                ) for problem_content in problem_list if (
                    not exists_problem_content_list.__contains__(
                        problem_content
                    ) if len(exists_problem_content_list) > 0 else True
                )
            ]

            QuerySet(Problem).bulk_create(problem_instance_list) if len(problem_instance_list) > 0 else None
            return [ProblemSerializer(problem_instance).data for problem_instance in problem_instance_list]

    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        content = serializers.CharField(required=False, label=_('content'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        def get_query_set(self):
            self.is_valid()
            query_set = QuerySet(model=Problem)
            query_set = query_set.filter(
                **{'knowledge_id': self.data.get('knowledge_id')})
            if 'content' in self.data:
                query_set = query_set.filter(**{'content__icontains': self.data.get('content')})
            query_set = query_set.order_by("-create_time")
            return query_set

        def list(self):
            query_set = self.get_query_set()
            return native_search(query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_problem.sql')))

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return native_page_search(current_page, page_size, query_set, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_problem.sql')))


def is_exits(exits_problem_paragraph_mapping_list, new_paragraph_mapping):
    filter_list = [exits_problem_paragraph_mapping for exits_problem_paragraph_mapping in
                   exits_problem_paragraph_mapping_list if
                   str(exits_problem_paragraph_mapping.paragraph_id) == new_paragraph_mapping.paragraph_id
                   and str(exits_problem_paragraph_mapping.problem_id) == new_paragraph_mapping.problem_id
                   and str(exits_problem_paragraph_mapping.knowledge_id) == new_paragraph_mapping.knowledge_id]
    return len(filter_list) > 0


def to_problem_paragraph_mapping(problem, document_id: str, paragraph_id: str, knowledge_id: str):
    return ProblemParagraphMapping(
        id=uuid.uuid7(),
        document_id=document_id,
        paragraph_id=paragraph_id,
        knowledge_id=knowledge_id,
        problem_id=str(problem.id)
    ), problem
