# coding=utf-8

from typing import Dict

import uuid_utils.compat as uuid
from celery_once import AlreadyQueued
from django.db import transaction
from django.db.models import QuerySet, Count, F
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import page_search
from common.event.listener_manage import ListenerManagement
from common.exception.app_exception import AppApiException
from common.utils.common import post
from knowledge.models import Paragraph, Problem, Document, ProblemParagraphMapping, SourceType, TaskType, State, \
    Knowledge
from knowledge.serializers.common import ProblemParagraphObject, ProblemParagraphManage, \
    get_embedding_model_id_by_knowledge_id, update_document_char_length, BatchSerializer
from knowledge.serializers.problem import ProblemInstanceSerializer, ProblemSerializer, ProblemSerializers
from knowledge.task.embedding import embedding_by_paragraph, enable_embedding_by_paragraph, \
    disable_embedding_by_paragraph, \
    delete_embedding_by_paragraph, embedding_by_problem as embedding_by_problem_task, delete_embedding_by_paragraph_ids, \
    embedding_by_problem, delete_embedding_by_source, update_embedding_document_id
from knowledge.task.generate import generate_related_by_paragraph_id_list


class ParagraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paragraph
        fields = ['id', 'content', 'is_active', 'document_id', 'title', 'create_time', 'update_time', 'position']


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


class ParagraphBatchGenerateRelatedSerializer(serializers.Serializer):
    paragraph_id_list = serializers.ListField(required=True, label=_('paragraph id list'),
                                              child=serializers.UUIDField(required=True, label=_('paragraph id')))
    model_id = serializers.UUIDField(required=True, label=_('model id'))
    prompt = serializers.CharField(required=True, label=_('prompt'), max_length=102400, allow_null=True,
                                   allow_blank=True)
    document_id = serializers.UUIDField(required=True, label=_('document id'))


class ParagraphSerializers(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=256, label=_('section title'), allow_null=True,
                                  allow_blank=True)
    content = serializers.CharField(required=True, max_length=102400, label=_('section title'))

    class Problem(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))
        paragraph_id = serializers.UUIDField(required=True, label=_('paragraph id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))
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
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(
                knowledge_id=self.data.get("knowledge_id"),
                paragraph_id=self.data.get(
                    'paragraph_id'))
            return [ProblemSerializer(row).data for row in
                    QuerySet(Problem).filter(id__in=[row.problem_id for row in problem_paragraph_mapping])]

        @transaction.atomic
        def save(self, instance: Dict, with_valid=True, with_embedding=True, embedding_by_problem=None):
            if with_valid:
                self.is_valid()
                ProblemInstanceSerializer(data=instance).is_valid(raise_exception=True)
            problem = QuerySet(Problem).filter(knowledge_id=self.data.get('knowledge_id'),
                                               content=instance.get('content')).first()
            if problem is None:
                problem = Problem(id=uuid.uuid7(), knowledge_id=self.data.get('knowledge_id'),
                                  content=instance.get('content'))
                problem.save()
            if QuerySet(ProblemParagraphMapping).filter(knowledge_id=self.data.get('knowledge_id'),
                                                        problem_id=problem.id,
                                                        paragraph_id=self.data.get('paragraph_id')).exists():
                raise AppApiException(500, _('Already associated, please do not associate again'))
            problem_paragraph_mapping = ProblemParagraphMapping(
                id=uuid.uuid7(),
                problem_id=problem.id,
                document_id=self.data.get('document_id'),
                paragraph_id=self.data.get('paragraph_id'),
                knowledge_id=self.data.get('knowledge_id')
            )
            problem_paragraph_mapping.save()
            model_id = get_embedding_model_id_by_knowledge_id(self.data.get('knowledge_id'))
            if with_embedding:
                embedding_by_problem_task({
                    'text': problem.content,
                    'is_active': True,
                    'source_type': SourceType.PROBLEM,
                    'source_id': problem_paragraph_mapping.id,
                    'document_id': self.data.get('document_id'),
                    'paragraph_id': self.data.get('paragraph_id'),
                    'knowledge_id': self.data.get('knowledge_id'),
                }, model_id)

            return ProblemSerializers.Operate(
                data={
                    'workspace_id':  self.data.get('workspace_id'),
                    'knowledge_id': self.data.get('knowledge_id'),
                    'problem_id': problem.id
                }
            ).one(with_valid=True)

    class Operate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        # 段落id
        paragraph_id = serializers.UUIDField(required=True, label=_('paragraph id'))
        # 知识库id
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        # 文档id
        document_id = serializers.UUIDField(required=True, label=_('document id'))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))
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
        workspace_id = serializers.CharField(required=True, label='Workspace ID')
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Document).filter(id=self.data.get('document_id'),
                                             knowledge_id=self.data.get('knowledge_id')).exists():
                raise AppApiException(500, _('The document id is incorrect'))

        @transaction.atomic
        def save(self, instance: Dict, with_valid=True, with_embedding=True):
            if with_valid:
                ParagraphSerializers(data=instance).is_valid(raise_exception=True)
                self.is_valid()
            knowledge_id = self.data.get("knowledge_id")
            document_id = self.data.get('document_id')

            # 先将同一文档中的所有段落位置向下移动一位
            Paragraph.objects.filter(document_id=document_id).update(position=F('position') + 1)

            paragraph_problem_model = self.get_paragraph_problem_model(knowledge_id, document_id, instance)
            paragraph = paragraph_problem_model.get('paragraph')
            problem_paragraph_object_list = paragraph_problem_model.get('problem_paragraph_object_list')
            problem_model_list, problem_paragraph_mapping_list = (
                ProblemParagraphManage(problem_paragraph_object_list, knowledge_id)
                .to_problem_model_list())
            # 新加的在最上面
            paragraph.position = 1
            paragraph.save()
            # 调整位置
            if 'position' in instance:
                if type(instance['position']) is not int:
                    instance['position'] = 1
            else:
                instance['position'] = 1

            ParagraphSerializers.AdjustPosition(data={
                'paragraph_id': str(paragraph.id),
                'knowledge_id': knowledge_id,
                'document_id': document_id,
                'workspace_id': self.data.get('workspace_id')
            }).adjust_position(instance.get('position'))
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
                ListenerManagement.update_status(
                    QuerySet(Document).filter(id=document_id), TaskType.EMBEDDING, State.SUCCESS
                )
                ListenerManagement.get_aggregation_document_status(document_id)()
            return ParagraphSerializers.Operate(
                data={
                    'paragraph_id': str(paragraph.id),
                    'knowledge_id': knowledge_id,
                    'document_id': document_id,
                    'workspace_id': self.data.get('workspace_id')
                }
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

    class Query(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))
        title = serializers.CharField(required=False, label=_('section title'))
        content = serializers.CharField(required=False)

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
            query_set = QuerySet(model=Paragraph)
            query_set = query_set.filter(
                **{'knowledge_id': self.data.get('knowledge_id'), 'document_id': self.data.get("document_id")})
            if 'title' in self.data:
                query_set = query_set.filter(
                    **{'title__icontains': self.data.get('title')})
            if 'content' in self.data:
                query_set = query_set.filter(**{'content__icontains': self.data.get('content')})
            query_set = query_set.order_by('position', 'create_time')
            return query_set

        def list(self):
            return list(map(lambda row: ParagraphSerializer(row).data, self.get_query_set()))

        def page(self, current_page, page_size):
            query_set = self.get_query_set()
            return page_search(current_page, page_size, query_set, lambda row: ParagraphSerializer(row).data)

    class Association(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        problem_id = serializers.UUIDField(required=True, label=_('problem id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))
        paragraph_id = serializers.UUIDField(required=True, label=_('paragraph id'))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            knowledge_id = self.data.get('knowledge_id')
            paragraph_id = self.data.get('paragraph_id')
            problem_id = self.data.get("problem_id")
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))
            if not QuerySet(Paragraph).filter(knowledge_id=knowledge_id, id=paragraph_id).exists():
                raise AppApiException(500, _('Paragraph does not exist'))
            if not QuerySet(Problem).filter(knowledge_id=knowledge_id, id=problem_id).exists():
                raise AppApiException(500, _('Problem does not exist'))

        def association(self, with_valid=True, with_embedding=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            # 已关联则直接返回
            if QuerySet(ProblemParagraphMapping).filter(
                knowledge_id=self.data.get('knowledge_id'),
                document_id=self.data.get('document_id'),
                paragraph_id=self.data.get('paragraph_id'),
                problem_id=self.data.get('problem_id')
            ).exists():
                return True

            problem = QuerySet(Problem).filter(id=self.data.get("problem_id")).first()
            problem_paragraph_mapping = ProblemParagraphMapping(id=uuid.uuid7(),
                                                                document_id=self.data.get('document_id'),
                                                                paragraph_id=self.data.get('paragraph_id'),
                                                                knowledge_id=self.data.get('knowledge_id'),
                                                                problem_id=problem.id)
            problem_paragraph_mapping.save()
            if with_embedding:
                model_id = get_embedding_model_id_by_knowledge_id(self.data.get('knowledge_id'))
                embedding_by_problem({
                    'text': problem.content,
                    'is_active': True,
                    'source_type': SourceType.PROBLEM,
                    'source_id': problem_paragraph_mapping.id,
                    'document_id': self.data.get('document_id'),
                    'paragraph_id': self.data.get('paragraph_id'),
                    'knowledge_id': self.data.get('knowledge_id'),
                }, model_id)

        def un_association(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            problem_paragraph_mapping = QuerySet(ProblemParagraphMapping).filter(
                paragraph_id=self.data.get('paragraph_id'),
                knowledge_id=self.data.get('knowledge_id'),
                problem_id=self.data.get(
                    'problem_id')).first()
            problem_paragraph_mapping_id = problem_paragraph_mapping.id
            problem_paragraph_mapping.delete()
            delete_embedding_by_source(problem_paragraph_mapping_id)
            return True

    class Batch(serializers.Serializer):
        workspace_id = serializers.CharField(required=False, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

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

        def batch_generate_related(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            paragraph_id_list = instance.get("paragraph_id_list")
            model_id = instance.get("model_id")
            prompt = instance.get("prompt")
            model_params_setting = instance.get("model_params_setting")
            document_id = self.data.get('document_id')
            ListenerManagement.update_status(
                QuerySet(Document).filter(id=document_id),
                TaskType.GENERATE_PROBLEM,
                State.PENDING
            )
            ListenerManagement.update_status(
                QuerySet(Paragraph).filter(id__in=paragraph_id_list),
                TaskType.GENERATE_PROBLEM,
                State.PENDING
            )
            ListenerManagement.get_aggregation_document_status(document_id)()
            try:
                generate_related_by_paragraph_id_list.delay(document_id, paragraph_id_list, model_id, model_params_setting, prompt)
            except AlreadyQueued as e:
                raise AppApiException(500, _('The task is being executed, please do not send it again.'))

    class Migrate(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))
        target_knowledge_id = serializers.UUIDField(required=True, label=_('target knowledge id'))
        target_document_id = serializers.UUIDField(required=True, label=_('target document id'))
        paragraph_id_list = serializers.ListField(required=True, label=_('paragraph id list'),
                                                  child=serializers.UUIDField(required=True, label=_('paragraph id')))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))
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
            knowledge_id = self.data.get('knowledge_id')
            target_knowledge_id = self.data.get('target_knowledge_id')
            document_id = self.data.get('document_id')
            target_document_id = self.data.get('target_document_id')
            paragraph_id_list = self.data.get('paragraph_id_list')
            paragraph_list = QuerySet(Paragraph).filter(knowledge_id=knowledge_id, document_id=document_id,
                                                        id__in=paragraph_id_list)
            problem_paragraph_mapping_list = QuerySet(ProblemParagraphMapping).filter(paragraph__in=paragraph_list)
            # 同数据集迁移
            if target_knowledge_id == knowledge_id:
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
                                             target_document_id, target_knowledge_id, None)
                # 修改段落信息
                paragraph_list.update(document_id=target_document_id)

                # 将当前文档中所有段落的位置向下移动，为新段落腾出空间
                Paragraph.objects.filter(document_id=target_document_id).exclude(
                    id__in=paragraph_id_list
                ).update(position=F('position') + len(paragraph_id_list))
                # 重新查询迁移的段落
                paragraph_list = Paragraph.objects.filter(
                    id__in=paragraph_id_list, document_id=target_document_id
                )
                # 将迁移的段落位置设置为从1开始的序号
                for i, paragraph in enumerate(paragraph_list):
                    paragraph.position = i + 1
                    paragraph.save()
            # 不同数据集迁移
            else:
                problem_list = QuerySet(Problem).filter(
                    id__in=[problem_paragraph_mapping.problem_id for problem_paragraph_mapping in
                            problem_paragraph_mapping_list])
                # 目标数据集问题
                target_problem_list = list(
                    QuerySet(Problem).filter(content__in=[problem.content for problem in problem_list],
                                             knowledge_id=target_knowledge_id))

                target_handle_problem_list = [
                    self.get_target_knowledge_problem(target_knowledge_id, target_document_id,
                                                      problem_paragraph_mapping,
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
                                                              ['problem_id', 'knowledge_id', 'document_id'])
                target_knowledge = QuerySet(Knowledge).filter(id=target_knowledge_id).first()
                knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
                embedding_model_id = None
                if target_knowledge.embedding_model_id != knowledge.embedding_model_id:
                    embedding_model_id = str(target_knowledge.embedding_model_id)
                pid_list = [paragraph.id for paragraph in paragraph_list]
                # 修改段落信息
                paragraph_list.update(knowledge_id=target_knowledge_id, document_id=target_document_id)

                # 将当前文档中所有段落的位置向下移动，为新段落腾出空间
                Paragraph.objects.filter(document_id=target_document_id).exclude(
                    id__in=pid_list
                ).update(position=F('position') + len(pid_list))
                # 重新查询迁移的段落
                paragraph_list = Paragraph.objects.filter(
                    id__in=pid_list, document_id=target_document_id
                )
                # 将迁移的段落位置设置为从1开始的序号
                for i, paragraph in enumerate(paragraph_list):
                    paragraph.position = i + 1
                    paragraph.save()
                # 修改向量段落信息
                update_embedding_document_id(pid_list, target_document_id, target_knowledge_id, embedding_model_id)

            update_document_char_length(document_id)
            update_document_char_length(target_document_id)

        @staticmethod
        def update_problem_paragraph_mapping(target_document_id: str, problem_paragraph_mapping):
            problem_paragraph_mapping.document_id = target_document_id
            return problem_paragraph_mapping

        @staticmethod
        def get_target_knowledge_problem(target_knowledge_id: str,
                                         target_document_id: str,
                                         problem_paragraph_mapping,
                                         source_problem_list,
                                         target_problem_list):
            source_problem_list = [source_problem for source_problem in source_problem_list if
                                   source_problem.id == problem_paragraph_mapping.problem_id]
            problem_paragraph_mapping.knowledge_id = target_knowledge_id
            problem_paragraph_mapping.document_id = target_document_id
            if len(source_problem_list) > 0:
                problem_content = source_problem_list[-1].content
                problem_list = [problem for problem in target_problem_list if problem.content == problem_content]
                if len(problem_list) > 0:
                    problem = problem_list[-1]
                    problem_paragraph_mapping.problem_id = problem.id
                    return problem, False
                else:
                    problem = Problem(id=uuid.uuid7(), knowledge_id=target_knowledge_id, content=problem_content)
                    target_problem_list.append(problem)
                    problem_paragraph_mapping.problem_id = problem.id
                    return problem, True
            return None

    class AdjustPosition(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))
        document_id = serializers.UUIDField(required=True, label=_('document id'))
        paragraph_id = serializers.UUIDField(required=True, label=_('paragraph id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            workspace_id = self.data.get('workspace_id')
            query_set = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id'))
            if workspace_id:
                query_set = query_set.filter(workspace_id=workspace_id)
            if not query_set.exists():
                raise AppApiException(500, _('Knowledge id does not exist'))

        @transaction.atomic
        def adjust_position(self, new_position):
            """
            调整段落顺序
            :param new_position: 新的顺序值
            """
            self.is_valid(raise_exception=True)
            try:
                new_position = int(new_position)
            except (TypeError, ValueError):
                raise serializers.ValidationError(_('new_position must be an integer'))
            # 获取当前段落
            paragraph = Paragraph.objects.get(id=self.data.get('paragraph_id'))
            old_position = paragraph.position

            if old_position < new_position:
                # 如果新顺序在当前顺序之后，更新受影响段落的顺序
                Paragraph.objects.filter(
                    position__gt=old_position, position__lte=new_position
                ).update(position=F('position') - 1)
            elif old_position > new_position:
                # 如果新顺序在当前顺序之前，更新受影响段落的顺序
                Paragraph.objects.filter(
                    position__lt=old_position, position__gte=new_position
                ).update(position=F('position') + 1)

            # 更新当前段落的顺序
            paragraph.position = new_position
            paragraph.save()


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
