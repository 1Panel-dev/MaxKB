# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_search_dataset_node.py
    @date：2024/6/4 11:56
    @desc:
"""
import os
from typing import List, Dict

from django.db import connection
from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.search_knowledge_node.i_search_knowledge_node import ISearchKnowledgeStepNode
from common.config.embedding_config import VectorStore
from common.constants.permission_constants import RoleConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.db.search import native_search
from common.utils.common import get_file_content
from knowledge.models import Document, Paragraph, Knowledge, SearchMode
from maxkb.conf import PROJECT_DIR
from models_provider.tools import get_model_instance_by_model_workspace_id


def get_embedding_id(dataset_id_list):
    dataset_list = QuerySet(Knowledge).filter(id__in=dataset_id_list)
    if len(set([dataset.embedding_model_id for dataset in dataset_list])) > 1:
        raise Exception("关联知识库的向量模型不一致，无法召回分段。")
    if len(dataset_list) == 0:
        raise Exception("知识库设置错误,请重新设置知识库")
    return dataset_list[0].embedding_model_id


def get_none_result(question):
    return NodeResult(
        {'paragraph_list': [], 'is_hit_handling_method': [], 'question': question, 'data': '',
         'directly_return': ''}, {})


def reset_title(title):
    if title is None or len(title.strip()) == 0:
        return ""
    else:
        return f"#### {title}\n"


def reset_meta(meta):
    if not meta.get('allow_download', False):
        return {'allow_download': False}
    return meta


class BaseSearchKnowledgeNode(ISearchKnowledgeStepNode):
    def save_context(self, details, workflow_manage):
        result = details.get('paragraph_list', [])
        knowledge_setting = self.node_params_serializer.data.get('knowledge_setting')
        directly_return = '\n'.join(
            [f"{paragraph.get('title', '')}:{paragraph.get('content')}" for paragraph in result if
             paragraph.get('is_hit_handling_method')])
        self.context['paragraph_list'] = result
        self.context['question'] = details.get('question')
        self.context['run_time'] = details.get('run_time')
        self.context['is_hit_handling_method_list'] = [row for row in result if row.get('is_hit_handling_method')]
        self.context['data'] = '\n'.join(
            [f"{paragraph.get('title', '')}:{paragraph.get('content')}" for paragraph in
             result])[0:knowledge_setting.get('max_paragraph_char_number', 5000)]
        self.context['directly_return'] = directly_return

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(fields[0], fields[1:])

    def execute(self, knowledge_id_list, knowledge_setting, question, show_knowledge, search_scope_type,
                search_scope_source,
                search_scope_reference,
                exclude_paragraph_id_list=None,
                **kwargs) -> NodeResult:
        self.context['question'] = question
        self.context['show_knowledge'] = show_knowledge

        document_id_list = None
        if search_scope_type == 'referencing':  # 引用上一步知识库/文档
            if search_scope_source == 'knowledge':  # 知识库
                knowledge_id_list = self.get_reference_content(search_scope_reference)
            else:  # 文档
                document_id_list = self.get_reference_content(search_scope_reference)
                knowledge_id_list = [str(k) for k in QuerySet(Document).filter(
                    id__in=document_id_list
                ).values_list(
                    'knowledge_id', flat=True
                ).distinct()]

        get_knowledge_list_of_authorized = DatabaseModelManage.get_model('get_knowledge_list_of_authorized')
        chat_user_type = self.workflow_manage.get_body().get('chat_user_type')
        if get_knowledge_list_of_authorized is not None and RoleConstants.CHAT_USER.value.name == chat_user_type:
            knowledge_id_list = get_knowledge_list_of_authorized(self.workflow_manage.get_body().get('chat_user_id'),
                                                                 knowledge_id_list)
        if len(knowledge_id_list) == 0:
            return get_none_result(question)
        model_id = get_embedding_id(knowledge_id_list)
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        embedding_model = get_model_instance_by_model_workspace_id(model_id, workspace_id)
        embedding_value = embedding_model.embed_query(question)
        vector = VectorStore.get_embedding_vector()
        exclude_document_id_list = [str(document.id) for document in
                                    QuerySet(Document).filter(
                                        knowledge_id__in=knowledge_id_list,
                                        is_active=False)]
        embedding_list = vector.query(question, embedding_value, knowledge_id_list, document_id_list,
                                      exclude_document_id_list,
                                      exclude_paragraph_id_list, True, knowledge_setting.get('top_n'),
                                      knowledge_setting.get('similarity'),
                                      SearchMode(knowledge_setting.get('search_mode')))
        # 手动关闭数据库连接
        connection.close()
        if embedding_list is None:
            return get_none_result(question)
        paragraph_list = self.list_paragraph(embedding_list, vector)
        result = [self.reset_paragraph(paragraph, embedding_list) for paragraph in paragraph_list]
        result = sorted(result, key=lambda p: p.get('similarity'), reverse=True)
        return NodeResult({'paragraph_list': result,
                           'is_hit_handling_method_list': [row for row in result if row.get('is_hit_handling_method')],
                           'data': '\n'.join(
                               [f"{reset_title(paragraph.get('title', ''))}{paragraph.get('content')}" for paragraph in
                                result])[0:knowledge_setting.get('max_paragraph_char_number', 5000)],
                           'directly_return': '\n'.join(
                               [paragraph.get('content') for paragraph in
                                result if
                                paragraph.get('is_hit_handling_method')]),
                           'question': question},

                          {})

    @staticmethod
    def reset_paragraph(paragraph: Dict, embedding_list: List):
        filter_embedding_list = [embedding for embedding in embedding_list if
                                 str(embedding.get('paragraph_id')) == str(paragraph.get('id'))]
        if filter_embedding_list is not None and len(filter_embedding_list) > 0:
            find_embedding = filter_embedding_list[-1]
            return {
                **paragraph,
                'similarity': find_embedding.get('similarity'),
                'is_hit_handling_method': find_embedding.get('similarity') > paragraph.get(
                    'directly_return_similarity') and paragraph.get('hit_handling_method') == 'directly_return',
                'update_time': paragraph.get('update_time').strftime("%Y-%m-%d %H:%M:%S"),
                'create_time': paragraph.get('create_time').strftime("%Y-%m-%d %H:%M:%S"),
                'id': str(paragraph.get('id')),
                'knowledge_id': str(paragraph.get('knowledge_id')),
                'document_id': str(paragraph.get('document_id')),
                'meta': reset_meta(paragraph.get('meta'))
            }

    @staticmethod
    def list_paragraph(embedding_list: List, vector):
        paragraph_id_list = [row.get('paragraph_id') for row in embedding_list]
        if paragraph_id_list is None or len(paragraph_id_list) == 0:
            return []
        paragraph_list = native_search(QuerySet(Paragraph).filter(id__in=paragraph_id_list),
                                       get_file_content(
                                           os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                        'list_knowledge_paragraph_by_paragraph_id.sql')),
                                       with_table_name=True)
        # 如果向量库中存在脏数据 直接删除
        if len(paragraph_list) != len(paragraph_id_list):
            exist_paragraph_list = [row.get('id') for row in paragraph_list]
            for paragraph_id in paragraph_id_list:
                if not exist_paragraph_list.__contains__(paragraph_id):
                    vector.delete_by_paragraph_id(paragraph_id)
        return paragraph_list

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            'show_knowledge': self.context.get('show_knowledge'),
            'question': self.context.get('question'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'paragraph_list': self.context.get('paragraph_list'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
