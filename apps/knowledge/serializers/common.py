# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： common_serializers.py
    @date：2023/11/17 11:00
    @desc:
"""
import os
import re
import zipfile
from typing import List

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.flow.tools import save_workflow_mapping, get_instance_resource, knowledge_instance_field_call_dict
from common.config.embedding_config import ModelManage
from common.db.search import native_search
from common.db.sql_execute import sql_execute, update_execute
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content
from common.utils.fork import Fork
from common.utils.logger import maxkb_logger
from knowledge.models import Document, KnowledgeWorkflow, KnowledgeWorkflowVersion, KnowledgeType
from knowledge.models import Paragraph, Problem, ProblemParagraphMapping, Knowledge, File, PageIndexNode, Embedding, SourceType
from maxkb.conf import PROJECT_DIR
from models_provider.tools import get_model, get_model_default_params
from system_manage.models.resource_mapping import ResourceMapping, ResourceType


class MetaSerializer(serializers.Serializer):
    class WebMeta(serializers.Serializer):
        source_url = serializers.CharField(required=True, label=_('source url'))
        selector = serializers.CharField(required=False, allow_null=True, allow_blank=True, label=_('selector'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)
            source_url = self.data.get('source_url')
            response = Fork(source_url, []).fork()
            if response.status == 500:
                raise AppApiException(500, _('URL error, cannot parse [{source_url}]').format(source_url=source_url))

    class BaseMeta(serializers.Serializer):
        # PageIndex检索模式配置
        search_mode = serializers.ChoiceField(
            required=False,
            choices=['traditional', 'page_index'],
            default='traditional',
            label=_('检索模式')
        )
        use_tree_filter = serializers.BooleanField(required=False, default=True, label=_('树过滤'))
        top_n = serializers.IntegerField(required=False, min_value=1, max_value=50, default=5, label=_('返回数量'))
        similarity_threshold = serializers.FloatField(required=False, min_value=0, max_value=1, default=0.6, label=_('相似度阈值'))

        def is_valid(self, *, raise_exception=False):
            super().is_valid(raise_exception=True)


class BatchSerializer(serializers.Serializer):
    id_list = serializers.ListField(required=True, child=serializers.UUIDField(required=True), label=_('id list'))

    def is_valid(self, *, model=None, raise_exception=False):
        super().is_valid(raise_exception=True)
        if model is not None:
            id_list = self.data.get('id_list')
            model_list = QuerySet(model).filter(id__in=id_list)
            if len(model_list) != len(id_list):
                model_id_list = [str(m.id) for m in model_list]
                error_id_list = list(filter(lambda row_id: not model_id_list.__contains__(row_id), id_list))
                raise AppApiException(500, _('The following id does not exist: {error_id_list}').format(
                    error_id_list=error_id_list))


class ProblemParagraphObject:
    def __init__(self, knowledge_id: str, document_id: str, paragraph_id: str, problem_content: str):
        self.knowledge_id = knowledge_id
        self.document_id = document_id
        self.paragraph_id = paragraph_id
        self.problem_content = problem_content


class GenerateRelatedSerializer(serializers.Serializer):
    model_id = serializers.UUIDField(required=True, label=_('Model id'))
    prompt = serializers.CharField(required=True, label=_('Prompt word'))
    state_list = serializers.ListField(required=False, child=serializers.CharField(required=True),
                                       label=_("state list"))


class ProblemParagraphManage:
    def __init__(self, problem_paragraph_object_list: List[ProblemParagraphObject], knowledge_id):
        self.knowledge_id = knowledge_id
        self.problem_paragraph_object_list = problem_paragraph_object_list

    def to_problem_model_list(self):
        problem_list = [item.problem_content for item in self.problem_paragraph_object_list]
        exists_problem_list = []
        if len(self.problem_paragraph_object_list) > 0:
            # 查询到已存在的问题列表
            exists_problem_list = QuerySet(Problem).filter(knowledge_id=self.knowledge_id,
                                                           content__in=problem_list).all()
        problem_content_dict = {}
        problem_model_list = [
            or_get(
                exists_problem_list,
                problemParagraphObject.problem_content,
                problemParagraphObject.knowledge_id,
                problemParagraphObject.document_id,
                problemParagraphObject.paragraph_id, problem_content_dict
            ) for problemParagraphObject in self.problem_paragraph_object_list]

        problem_paragraph_mapping_list = [
            ProblemParagraphMapping(
                id=uuid.uuid7(),
                document_id=document_id,
                problem_id=problem_model.id,
                paragraph_id=paragraph_id,
                knowledge_id=self.knowledge_id
            ) for problem_model, document_id, paragraph_id in problem_model_list]

        result = [
            problem_model for problem_model, is_create in problem_content_dict.values() if is_create
        ], problem_paragraph_mapping_list
        return result


def get_embedding_model_by_knowledge_id_list(knowledge_id_list: List):
    knowledge_list = QuerySet(Knowledge).filter(id__in=knowledge_id_list)
    if len(set([knowledge.embedding_model_id for knowledge in knowledge_list])) > 1:
        raise Exception(_('The knowledge base is inconsistent with the vector model'))
    if len(knowledge_list) == 0:
        raise Exception(_('Knowledge base setting error, please reset the knowledge base'))

    default_params = get_model_default_params(knowledge_list[0].embedding_model)

    return ModelManage.get_model(
        str(knowledge_list[0].embedding_model_id),
        lambda _id: get_model(knowledge_list[0].embedding_model, **{**default_params})
    )


def get_embedding_model_by_knowledge_id(knowledge_id: str):
    knowledge = QuerySet(Knowledge).select_related('embedding_model').filter(id=knowledge_id).first()

    default_params = get_model_default_params(knowledge.embedding_model)

    return ModelManage.get_model(str(knowledge.embedding_model_id),
                                 lambda _id: get_model(knowledge.embedding_model, **{**default_params}))


def get_embedding_model_by_knowledge(knowledge):
    default_params = get_model_default_params(knowledge.embedding_model)

    return ModelManage.get_model(str(knowledge.embedding_model_id),
                                 lambda _id: get_model(knowledge.embedding_model, **{**default_params}))


def get_embedding_model_id_by_knowledge_id(knowledge_id):
    knowledge = QuerySet(Knowledge).select_related('embedding_model').filter(id=knowledge_id).first()
    return str(knowledge.embedding_model_id)


def get_embedding_model_id_by_knowledge_id_list(knowledge_id_list: List):
    knowledge_list = QuerySet(Knowledge).filter(id__in=knowledge_id_list)
    if len(set([knowledge.embedding_model_id for knowledge in knowledge_list])) > 1:
        raise Exception(_('The knowledge base is inconsistent with the vector model'))
    if len(knowledge_list) == 0:
        raise Exception(_('Knowledge base setting error, please reset the knowledge base'))
    return str(knowledge_list[0].embedding_model_id)


def zip_dir(zip_path, output=None):
    output = output or os.path.basename(zip_path) + '.zip'
    zip = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(zip_path):
        relative_root = '' if root == zip_path else root.replace(zip_path, '') + os.sep
        for filename in files:
            zip.write(os.path.join(root, filename), relative_root + filename)
    zip.close()


def is_valid_uuid(s):
    try:
        uuid.UUID(s)
        return True
    except ValueError:
        return False


def write_image(zip_path: str, image_list: List[str]):
    for image in image_list:
        search = re.search("\(.*\)", image)
        if search:
            text = search.group()
            if text.startswith('(./oss/file/'):
                r = text.replace('(./oss/file/', '').replace(')', '')
                r = r.strip().split(" ")[0]
                if not is_valid_uuid(r):
                    break
                file = QuerySet(File).filter(id=r).first()
                if file is None:
                    break
                zip_inner_path = os.path.join('oss', 'file', r)
                file_path = os.path.join(zip_path, zip_inner_path)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                with open(os.path.join(zip_path, file_path), 'wb') as f:
                    f.write(file.get_bytes())


def update_document_char_length(document_id: str):
    update_execute(get_file_content(
        os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'update_document_char_length.sql')),
        (document_id, document_id))


def list_paragraph(paragraph_list: List[str]):
    if paragraph_list is None or len(paragraph_list) == 0:
        return []
    return native_search(QuerySet(Paragraph).filter(id__in=paragraph_list), get_file_content(
        os.path.join(PROJECT_DIR, "apps", "knowledge", 'sql', 'list_paragraph.sql')))


def or_get(exists_problem_list, content, knowledge_id, document_id, paragraph_id, problem_content_dict):
    if content in problem_content_dict:
        return problem_content_dict.get(content)[0], document_id, paragraph_id
    exists = [row for row in exists_problem_list if row.content == content]
    if len(exists) > 0:
        problem_content_dict[content] = exists[0], False
        return exists[0], document_id, paragraph_id
    else:
        problem = Problem(id=uuid.uuid7(), content=content, knowledge_id=knowledge_id)
        problem_content_dict[content] = problem, True
        return problem, document_id, paragraph_id


def get_knowledge_operation_object(knowledge_id: str):
    knowledge_model = QuerySet(model=Knowledge).filter(id=knowledge_id).first()
    if knowledge_model is not None:
        return {
            "name": knowledge_model.name,
            "desc": knowledge_model.desc,
            "type": knowledge_model.type,
            "create_time": knowledge_model.create_time,
            "update_time": knowledge_model.update_time
        }
    return {}


def create_knowledge_index(knowledge_id=None, document_id=None):
    if knowledge_id is None and document_id is None:
        raise AppApiException(500, _('Knowledge ID or Document ID must be provided'))

    if knowledge_id is not None:
        k_id = knowledge_id
    else:
        document = QuerySet(Document).filter(id=document_id).first()
        k_id = document.knowledge_id

    sql = f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'embedding' AND indexname = 'embedding_hnsw_idx_{k_id}'"
    index = sql_execute(sql, [])
    if not index:
        sql = f"SELECT vector_dims(embedding) AS dims FROM embedding WHERE knowledge_id = '{k_id}' LIMIT 1"
        result = sql_execute(sql, [])
        if len(result) == 0:
            return
        dims = result[0]['dims']
        # 超过2000维度不创建索引，pgvector hnsw索引不支持超过2000维度
        if dims < 2000:
            sql = f"""CREATE INDEX "embedding_hnsw_idx_{k_id}" ON embedding USING hnsw ((embedding::vector({dims})) vector_cosine_ops) WHERE knowledge_id = '{k_id}'"""
            update_execute(sql, [])
            maxkb_logger.info(f'Created index for knowledge ID: {k_id}')





def _build_page_index_after_paragraph_creation(document_ids: List[str]):
    """
    在段落创建后自动构建PageIndex（不依赖向量化状态）
    这是PageIndex的正确触发时机：段落创建完成后立即构建，不等待向量化。

    Args:
        document_ids: 文档ID列表
    """
    from knowledge.models import Document, PageIndexNode, Paragraph, Embedding, SourceType

    for doc_id in document_ids:
        document = QuerySet(Document).filter(id=doc_id).first()
        if not document:
            continue

        knowledge = document.knowledge

        # 检查PageIndex是否启用
        try:
            from config.page_index_config import PageIndexConfig
            if not PageIndexConfig.is_enabled(str(knowledge.id)):
                continue
        except ImportError:
            continue

        # 检查是否已有段落
        paragraph_count = QuerySet(Paragraph).filter(document=document).count()
        if paragraph_count == 0:
            continue

        # 构建PageIndex（不等待向量化）
        try:
            maxkb_logger.info(f'[PageIndex] Auto building for document: {document.name} (ID: {doc_id})')

            # 导入PageIndex构建器
            from knowledge.page_index import PageIndex

            # 清理当前文档旧PageIndex节点
            QuerySet(PageIndexNode).filter(document=document).delete()

            # 构建PageIndex树
            page_index = PageIndex.from_documents(
                documents=[document],
                knowledge=knowledge,
                chunk_size=1000,
                chunk_overlap=200
            )

            # 同步段落向量与PageIndex节点关系
            _sync_page_index_embeddings_for_document(document)

            stats = page_index.get_statistics()
            maxkb_logger.info(
                f'[PageIndex] Built successfully for document {doc_id}: '
                f'{stats["total_nodes"]} nodes, max depth {stats["max_depth"]}'
            )

        except Exception as e:
            maxkb_logger.error(f'[PageIndex] Build error for document {doc_id}: {str(e)}', exc_info=True)


def _build_page_index_for_document_if_needed(document: Document):
    """
    在向量化之前构建PageIndex（如果需要且尚未构建）
    这确保了在生成embedding时，page_index_node表已经有数据
    """
    knowledge = document.knowledge

    # 检查PageIndex是否启用
    try:
        from config.page_index_config import PageIndexConfig
        if not PageIndexConfig.is_enabled(str(knowledge.id)):
            return
    except ImportError:
        return

    # 检查是否已有段落
    paragraph_count = QuerySet(Paragraph).filter(document=document).count()
    if paragraph_count == 0:
        return

    # 检查是否已经构建过PageIndex
    existing_nodes = QuerySet(PageIndexNode).filter(document=document).count()
    if existing_nodes > 0:
        maxkb_logger.info(f'[PageIndex] Already built for document {document.id}, skipping')
        return

    # 构建PageIndex
    try:
        maxkb_logger.info(f'[PageIndex] Building for document: {document.name} (ID: {document.id})')

        from knowledge.page_index import PageIndex

        page_index = PageIndex.from_documents(
            documents=[document],
            knowledge=knowledge,
            chunk_size=1000,
            chunk_overlap=200
        )

        stats = page_index.get_statistics()
        maxkb_logger.info(
            f'[PageIndex] Built successfully for document {document.id}: '
            f'{stats["total_nodes"]} nodes, max depth {stats["max_depth"]}'
        )
    except Exception as e:
        maxkb_logger.error(f'[PageIndex] Build error for document {document.id}: {str(e)}', exc_info=True)


def _sync_page_index_embeddings_for_document(document: Document):
    """
    将段落向量与PageIndex节点进行绑定，补齐page_index_node/tree_path等字段
    """
    nodes = list(QuerySet(PageIndexNode).filter(document=document).values(
        'id', 'title', 'level', 'path', 'order'
    ))
    if not nodes:
        return None

    root_node = None
    node_by_title = {}
    for node in nodes:
        if root_node is None and node.get('level') == 0:
            root_node = node
        title = (node.get('title') or '').strip()
        if title and title not in node_by_title:
            node_by_title[title] = node

    updated_count = 0
    paragraph_list = list(QuerySet(Paragraph).filter(document=document).values('id', 'title'))
    for paragraph in paragraph_list:
        title = (paragraph.get('title') or '').strip()
        node = node_by_title.get(title) if title else None
        if node is None:
            node = root_node
        if not node:
            continue

        updated_count += QuerySet(Embedding).filter(
            paragraph_id=paragraph.get('id'),
            source_type=SourceType.PARAGRAPH
        ).update(
            page_index_node_id=node.get('id'),
            tree_level=node.get('level', 0),
            tree_path=node.get('path', []),
            sibling_index=node.get('order', 0)
        )

    fallback_updated = 0
    if updated_count == 0 and root_node:
        fallback_updated = QuerySet(Embedding).filter(
            document_id=document.id,
            source_type=SourceType.PARAGRAPH,
            page_index_node_id__isnull=True
        ).update(
            page_index_node_id=root_node.get('id'),
            tree_level=root_node.get('level', 0),
            tree_path=root_node.get('path', []),
            sibling_index=root_node.get('order', 0)
        )

    result = {
        'document_id': str(document.id),
        'paragraphs': len(paragraph_list),
        'updated': updated_count,
        'fallback_updated': fallback_updated,
        'root_node_id': root_node.get('id') if root_node else None
    }
    maxkb_logger.info(
        f"[PageIndex] 同步段落向量与节点关系完成 document={document.id} "
        f"paragraphs={result['paragraphs']} updated={result['updated']} "
        f"fallback_updated={result['fallback_updated']} root_node={result['root_node_id']}"
    )
    return result


def drop_knowledge_index(knowledge_id=None, document_id=None):

    if knowledge_id is None and document_id is None:
        raise AppApiException(500, _('Knowledge ID or Document ID must be provided'))

    if knowledge_id is not None:
        k_id = knowledge_id
    else:
        document = QuerySet(Document).filter(id=document_id).first()
        k_id = document.knowledge_id

    sql = f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'embedding' AND indexname = 'embedding_hnsw_idx_{k_id}'"
    index = sql_execute(sql, [])
    if index:
        sql = f'DROP INDEX "embedding_hnsw_idx_{k_id}"'
        update_execute(sql, [])
        maxkb_logger.info(f'Dropped index for knowledge ID: {k_id}')


def update_resource_mapping_by_knowledge(knowledge_id: str):
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
    instance_mapping = get_instance_resource(knowledge, ResourceType.KNOWLEDGE, str(knowledge.id),
                                             knowledge_instance_field_call_dict)
    if knowledge.type == KnowledgeType.WORKFLOW:
        knowledge_workflow = QuerySet(KnowledgeWorkflow).filter(
            knowledge_id=knowledge_id).order_by(
            '-create_time')[0:1].first()
        if knowledge_workflow:
            save_workflow_mapping(knowledge_workflow.work_flow, ResourceType.KNOWLEDGE,
                                  str(knowledge_id), instance_mapping)
            return
    else:
        save_workflow_mapping({}, ResourceType.KNOWLEDGE,
                              str(knowledge_id), instance_mapping)
