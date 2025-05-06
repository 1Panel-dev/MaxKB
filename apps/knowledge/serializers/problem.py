import os
from typing import Dict

from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import native_search
from common.utils.common import get_file_content
from knowledge.models import Problem, ProblemParagraphMapping, Paragraph, Knowledge
from knowledge.serializers.common import get_embedding_model_id_by_knowledge_id
from knowledge.task.embedding import delete_embedding_by_source_ids, update_problem_embedding
from maxkb.const import PROJECT_DIR


class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'content', 'knowledge_id', 'create_time', 'update_time']


class ProblemInstanceSerializer(serializers.Serializer):
    id = serializers.CharField(required=False, label=_('problem id'))
    content = serializers.CharField(required=True, max_length=256, label=_('content'))


class ProblemSerializers(serializers.Serializer):
    class Operate(serializers.Serializer):
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        problem_id = serializers.UUIDField(required=True, label=_('problem id'))

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
