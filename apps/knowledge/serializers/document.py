import os
from functools import reduce
from typing import Dict, List

import uuid_utils.compat as uuid
from celery_once import AlreadyQueued
from django.db import transaction
from django.db.models import QuerySet, Model
from django.db.models.functions import Substr, Reverse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.db.search import native_search
from common.event import ListenerManagement
from common.event.common import work_thread_pool
from common.exception.app_exception import AppApiException
from common.handle.impl.text.csv_split_handle import CsvSplitHandle
from common.handle.impl.text.doc_split_handle import DocSplitHandle
from common.handle.impl.text.html_split_handle import HTMLSplitHandle
from common.handle.impl.text.pdf_split_handle import PdfSplitHandle
from common.handle.impl.text.text_split_handle import TextSplitHandle
from common.handle.impl.text.xls_split_handle import XlsSplitHandle
from common.handle.impl.text.xlsx_split_handle import XlsxSplitHandle
from common.handle.impl.text.zip_split_handle import ZipSplitHandle
from common.utils.common import post, get_file_content, bulk_create_in_batches
from knowledge.models import Knowledge, Paragraph, Problem, Document, KnowledgeType, ProblemParagraphMapping, State, \
    TaskType, File
from knowledge.serializers.common import ProblemParagraphManage, BatchSerializer
from knowledge.serializers.paragraph import ParagraphSerializers, ParagraphInstanceSerializer, \
    delete_problems_and_mappings
from knowledge.task import embedding_by_document, delete_embedding_by_document_list
from maxkb.const import PROJECT_DIR

default_split_handle = TextSplitHandle()
split_handles = [
    HTMLSplitHandle(),
    DocSplitHandle(),
    PdfSplitHandle(),
    XlsxSplitHandle(),
    XlsSplitHandle(),
    CsvSplitHandle(),
    ZipSplitHandle(),
    default_split_handle
]


class BatchCancelInstanceSerializer(serializers.Serializer):
    id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True), label=('id list'))
    type = serializers.IntegerField(required=True, label=_('task type'))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        _type = self.data.get('type')
        try:
            TaskType(_type)
        except Exception as e:
            raise AppApiException(500, _('task type not support'))


class DocumentInstanceSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('document name'), max_length=128, min_length=1)
    paragraphs = ParagraphInstanceSerializer(required=False, many=True, allow_null=True)


class DocumentCreateRequest(serializers.Serializer):
    name = serializers.CharField(required=True, label=_('knowledge name'), max_length=64, min_length=1)
    desc = serializers.CharField(required=True, label=_('knowledge description'), max_length=256, min_length=1)
    embedding_model_id = serializers.UUIDField(required=True, label=_('embedding model'))
    documents = DocumentInstanceSerializer(required=False, many=True)


class DocumentSplitRequest(serializers.Serializer):
    file = serializers.ListField(required=True, label=_('file list'))
    limit = serializers.IntegerField(required=False, label=_('limit'))
    patterns = serializers.ListField(
        required=False,
        child=serializers.CharField(required=True, label=_('patterns')),
        label=_('patterns')
    )
    with_filter = serializers.BooleanField(required=False, label=_('Auto Clean'))


class DocumentBatchRequest(serializers.Serializer):
    file = serializers.ListField(required=True, label=_('file list'))
    limit = serializers.IntegerField(required=False, label=_('limit'))
    patterns = serializers.ListField(
        required=False,
        child=serializers.CharField(required=True, label=_('patterns')),
        label=_('patterns')
    )
    with_filter = serializers.BooleanField(required=False, label=_('Auto Clean'))


class DocumentSerializers(serializers.Serializer):
    class Operate(serializers.Serializer):
        document_id = serializers.UUIDField(required=True, label=_('document id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            document_id = self.data.get('document_id')
            if not QuerySet(Document).filter(id=document_id).exists():
                raise AppApiException(500, _('document id not exist'))

        def one(self, with_valid=False):
            if with_valid:
                self.is_valid(raise_exception=True)
            query_set = QuerySet(model=Document)
            query_set = query_set.filter(**{'id': self.data.get("document_id")})
            return native_search({
                'document_custom_sql': query_set,
                'order_by_query': QuerySet(Document).order_by('-create_time', 'id')
            }, select_string=get_file_content(
                os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_document.sql')), with_search_one=True)

        def refresh(self, state_list=None, with_valid=True):
            if state_list is None:
                state_list = [State.PENDING.value, State.STARTED.value, State.SUCCESS.value, State.FAILURE.value,
                              State.REVOKE.value,
                              State.REVOKED.value, State.IGNORED.value]
            if with_valid:
                self.is_valid(raise_exception=True)
            knowledge = QuerySet(Knowledge).filter(id=self.data.get('knowledge_id')).first()
            embedding_model_id = knowledge.embedding_model_id
            knowledge_user_id = knowledge.user_id
            embedding_model = QuerySet(Model).filter(id=embedding_model_id).first()
            if embedding_model is None:
                raise AppApiException(500, _('Model does not exist'))
            if embedding_model.permission_type == 'PRIVATE' and knowledge_user_id != embedding_model.user_id:
                raise AppApiException(500, _('No permission to use this model') + f"{embedding_model.name}")
            document_id = self.data.get("document_id")
            ListenerManagement.update_status(
                QuerySet(Document).filter(id=document_id), TaskType.EMBEDDING, State.PENDING
            )
            ListenerManagement.update_status(
                QuerySet(Paragraph).annotate(
                    reversed_status=Reverse('status'),
                    task_type_status=Substr('reversed_status', TaskType.EMBEDDING.value, 1),
                ).filter(task_type_status__in=state_list, document_id=document_id).values('id'),
                TaskType.EMBEDDING,
                State.PENDING
            )
            ListenerManagement.get_aggregation_document_status(document_id)()

            try:
                embedding_by_document.delay(document_id, embedding_model_id, state_list)
            except AlreadyQueued as e:
                raise AppApiException(500, _('The task is being executed, please do not send it repeatedly.'))

    class Create(serializers.Serializer):
        knowledge_id = serializers.UUIDField(required=True, label=_('document id'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            if not QuerySet(Knowledge).filter(id=self.data.get('knowledge_id')).exists():
                raise AppApiException(10000, _('knowledge id not exist'))
            return True

        @staticmethod
        def post_embedding(result, document_id, knowledge_id):
            DocumentSerializers.Operate(
                data={'knowledge_id': knowledge_id, 'document_id': document_id}).refresh()
            return result

        @post(post_function=post_embedding)
        @transaction.atomic
        def save(self, instance: Dict, with_valid=False, **kwargs):
            if with_valid:
                DocumentCreateRequest(data=instance).is_valid(raise_exception=True)
                self.is_valid(raise_exception=True)
            knowledge_id = self.data.get('knowledge_id')
            document_paragraph_model = self.get_document_paragraph_model(knowledge_id, instance)

            document_model = document_paragraph_model.get('document')
            paragraph_model_list = document_paragraph_model.get('paragraph_model_list')
            problem_paragraph_object_list = document_paragraph_model.get('problem_paragraph_object_list')
            problem_model_list, problem_paragraph_mapping_list = (
                ProblemParagraphManage(problem_paragraph_object_list, knowledge_id).to_problem_model_list())
            # 插入文档
            document_model.save()
            # 批量插入段落
            QuerySet(Paragraph).bulk_create(paragraph_model_list) if len(paragraph_model_list) > 0 else None
            # 批量插入问题
            QuerySet(Problem).bulk_create(problem_model_list) if len(problem_model_list) > 0 else None
            # 批量插入关联问题
            QuerySet(ProblemParagraphMapping).bulk_create(
                problem_paragraph_mapping_list
            ) if len(problem_paragraph_mapping_list) > 0 else None
            document_id = str(document_model.id)
            return (DocumentSerializers.Operate(
                data={'knowledge_id': knowledge_id, 'document_id': document_id}
            ).one(with_valid=True), document_id, knowledge_id)

        @staticmethod
        def get_paragraph_model(document_model, paragraph_list: List):
            knowledge_id = document_model.knowledge_id
            paragraph_model_dict_list = [
                ParagraphSerializers.Create(
                    data={
                        'knowledge_id': knowledge_id, 'document_id': str(document_model.id)
                    }).get_paragraph_problem_model(knowledge_id, document_model.id, paragraph)
                for paragraph in paragraph_list]

            paragraph_model_list = []
            problem_paragraph_object_list = []
            for paragraphs in paragraph_model_dict_list:
                paragraph = paragraphs.get('paragraph')
                for problem_model in paragraphs.get('problem_paragraph_object_list'):
                    problem_paragraph_object_list.append(problem_model)
                paragraph_model_list.append(paragraph)

            return {
                'document': document_model,
                'paragraph_model_list': paragraph_model_list,
                'problem_paragraph_object_list': problem_paragraph_object_list
            }

        @staticmethod
        def get_document_paragraph_model(knowledge_id, instance: Dict):
            document_model = Document(
                **{
                    'knowledge_id': knowledge_id,
                    'id': uuid.uuid7(),
                    'name': instance.get('name'),
                    'char_length': reduce(
                        lambda x, y: x + y,
                        [len(p.get('content')) for p in instance.get('paragraphs', [])],
                        0),
                    'meta': instance.get('meta') if instance.get('meta') is not None else {},
                    'type': instance.get('type') if instance.get('type') is not None else KnowledgeType.BASE
                })

            return DocumentSerializers.Create.get_paragraph_model(
                document_model,
                instance.get('paragraphs') if 'paragraphs' in instance else []
            )

    class Split(serializers.Serializer):
        workspace_id = serializers.CharField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        def is_valid(self, *, raise_exception=True):
            super().is_valid(raise_exception=True)
            files = self.data.get('file')
            for f in files:
                if f.size > 1024 * 1024 * 100:
                    raise AppApiException(500, _(
                        'The maximum size of the uploaded file cannot exceed {}MB'
                    ).format(100))

        def parse(self, instance):
            self.is_valid(raise_exception=True)
            DocumentSplitRequest(instance).is_valid(raise_exception=True)

            file_list = instance.get("file")
            return reduce(
                lambda x, y: [*x, *y],
                [self.file_to_paragraph(
                    f,
                    instance.get("patterns", None),
                    instance.get("with_filter", None),
                    instance.get("limit", 4096)
                ) for f in file_list],
                []
            )

        def save_image(self, image_list):
            if image_list is not None and len(image_list) > 0:
                exist_image_list = [str(i.get('id')) for i in
                                    QuerySet(File).filter(id__in=[i.id for i in image_list]).values('id')]
                save_image_list = [image for image in image_list if not exist_image_list.__contains__(str(image.id))]
                save_image_list = list({img.id: img for img in save_image_list}.values())
                # save image
                for file in save_image_list:
                    file_bytes = file.meta.pop('content')
                    file.workspace_id = self.data.get('workspace_id')
                    file.meta['knowledge_id'] = self.data.get('knowledge_id')
                    file.save(file_bytes)

        def file_to_paragraph(self, file, pattern_list: List, with_filter: bool, limit: int):
            get_buffer = FileBufferHandle().get_buffer
            for split_handle in split_handles:
                if split_handle.support(file, get_buffer):
                    result = split_handle.handle(file, pattern_list, with_filter, limit, get_buffer, self.save_image)
                    if isinstance(result, list):
                        return result
                    return [result]
            result = default_split_handle.handle(file, pattern_list, with_filter, limit, get_buffer, self.save_image)
            if isinstance(result, list):
                return result
            return [result]

    class Batch(serializers.Serializer):
        workspace_id = serializers.UUIDField(required=True, label=_('workspace id'))
        knowledge_id = serializers.UUIDField(required=True, label=_('knowledge id'))

        @staticmethod
        def post_embedding(document_list, knowledge_id):
            for document_dict in document_list:
                DocumentSerializers.Operate(
                    data={'knowledge_id': knowledge_id, 'document_id': document_dict.get('id')}).refresh()
            return document_list

        @post(post_function=post_embedding)
        @transaction.atomic
        def batch_save(self, instance_list: List[Dict], with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            DocumentInstanceSerializer(many=True, data=instance_list).is_valid(raise_exception=True)
            knowledge_id = self.data.get("knowledge_id")
            document_model_list = []
            paragraph_model_list = []
            problem_paragraph_object_list = []
            # 插入文档
            for document in instance_list:
                document_paragraph_dict_model = DocumentSerializers.Create.get_document_paragraph_model(knowledge_id,
                                                                                                        document)
                document_model_list.append(document_paragraph_dict_model.get('document'))
                for paragraph in document_paragraph_dict_model.get('paragraph_model_list'):
                    paragraph_model_list.append(paragraph)
                for problem_paragraph_object in document_paragraph_dict_model.get('problem_paragraph_object_list'):
                    problem_paragraph_object_list.append(problem_paragraph_object)

            problem_model_list, problem_paragraph_mapping_list = (
                ProblemParagraphManage(problem_paragraph_object_list, knowledge_id).to_problem_model_list()
            )
            # 插入文档
            QuerySet(Document).bulk_create(document_model_list) if len(document_model_list) > 0 else None
            # 批量插入段落
            bulk_create_in_batches(Paragraph, paragraph_model_list, batch_size=1000)
            # 批量插入问题
            bulk_create_in_batches(Problem, problem_model_list, batch_size=1000)
            # 批量插入关联问题
            bulk_create_in_batches(ProblemParagraphMapping, problem_paragraph_mapping_list, batch_size=1000)
            # 查询文档
            query_set = QuerySet(model=Document)
            if len(document_model_list) == 0:
                return [], knowledge_id
            query_set = query_set.filter(**{'id__in': [d.id for d in document_model_list]})
            return native_search(
                {
                    'document_custom_sql': query_set,
                    'order_by_query': QuerySet(Document).order_by('-create_time', 'id')
                },
                select_string=get_file_content(
                    os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_document.sql')
                ),
                with_search_one=False
            ), knowledge_id

        @staticmethod
        def _batch_sync(document_id_list: List[str]):
            for document_id in document_id_list:
                DocumentSerializers.Sync(data={'document_id': document_id}).sync()

        def batch_sync(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Document, raise_exception=True)
                self.is_valid(raise_exception=True)
            # 异步同步
            work_thread_pool.submit(self._batch_sync, instance.get('id_list'))
            return True

        @transaction.atomic
        def batch_delete(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Document, raise_exception=True)
                self.is_valid(raise_exception=True)
            document_id_list = instance.get("id_list")
            QuerySet(Document).filter(id__in=document_id_list).delete()
            QuerySet(Paragraph).filter(document_id__in=document_id_list).delete()
            delete_problems_and_mappings(document_id_list)
            # 删除向量库
            delete_embedding_by_document_list(document_id_list)
            return True

        def batch_cancel(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
                BatchCancelInstanceSerializer(data=instance).is_valid(raise_exception=True)
            document_id_list = instance.get("id_list")
            ListenerManagement.update_status(
                QuerySet(Paragraph).annotate(
                    reversed_status=Reverse('status'),
                    task_type_status=Substr('reversed_status', TaskType(instance.get('type')).value, 1),
                ).filter(
                    task_type_status__in=[State.PENDING.value, State.STARTED.value]
                ).filter(
                    document_id__in=document_id_list
                ).values('id'),
                TaskType(instance.get('type')),
                State.REVOKE
            )
            ListenerManagement.update_status(
                QuerySet(Document).annotate(
                    reversed_status=Reverse('status'),
                    task_type_status=Substr('reversed_status', TaskType(instance.get('type')).value, 1),
                ).filter(
                    task_type_status__in=[State.PENDING.value, State.STARTED.value]
                ).filter(
                    id__in=document_id_list
                ).values('id'),
                TaskType(instance.get('type')),
                State.REVOKE
            )

        def batch_edit_hit_handling(self, instance: Dict, with_valid=True):
            if with_valid:
                BatchSerializer(data=instance).is_valid(model=Document, raise_exception=True)
                hit_handling_method = instance.get('hit_handling_method')
                if hit_handling_method is None:
                    raise AppApiException(500, _('Hit handling method is required'))
                if hit_handling_method != 'optimization' and hit_handling_method != 'directly_return':
                    raise AppApiException(500, _('The hit processing method must be directly_return|optimization'))
                self.is_valid(raise_exception=True)
            document_id_list = instance.get("id_list")
            hit_handling_method = instance.get('hit_handling_method')
            directly_return_similarity = instance.get('directly_return_similarity')
            update_dict = {'hit_handling_method': hit_handling_method}
            if directly_return_similarity is not None:
                update_dict['directly_return_similarity'] = directly_return_similarity
            QuerySet(Document).filter(id__in=document_id_list).update(**update_dict)

        def batch_refresh(self, instance: Dict, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            document_id_list = instance.get("id_list")
            state_list = instance.get("state_list")
            knowledge_id = self.data.get('knowledge_id')
            for document_id in document_id_list:
                try:
                    DocumentSerializers.Operate(
                        data={'knowledge_id': knowledge_id, 'document_id': document_id}).refresh(state_list)
                except AlreadyQueued as e:
                    pass


class FileBufferHandle:
    buffer = None

    def get_buffer(self, file):
        if self.buffer is None:
            self.buffer = file.read()
        return self.buffer
