# coding=utf-8
from typing import List

import jieba
from django.db.models import Q
from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.search_document_node.i_search_document_node import ISearchDocumentStepNode
from common.constants.permission_constants import RoleConstants
from common.database_model_manage.database_model_manage import DatabaseModelManage
from knowledge.models import Document, DocumentTag, Knowledge


class BaseSearchDocumentNode(ISearchDocumentStepNode):
    def save_context(self, details, workflow_manage):
        self.context['document_list'] = details.get('document_list')
        self.context['knowledge_list'] = details.get('knowledge_list')
        self.context['document_items'] = details.get('document_items')
        self.context['knowledge_items'] = details.get('knowledge_items')
        self.context['question'] = details.get('question')
        self.context['run_time'] = details.get('run_time')
        self.context['exception_message'] = details.get('err_message')

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(fields[0], fields[1:])

    def execute(self, knowledge_id_list: List, search_mode: str, search_scope_type: str, search_scope_source: str,
                search_scope_reference: List, question_reference: List, search_condition_type: str,
                search_condition_list: List,
                **kwargs) -> NodeResult:

        if search_scope_type == 'custom':  # 手动选择知识库
            document_id_list = QuerySet(Document).filter(
                knowledge_id__in=knowledge_id_list
            ).values_list('id', flat=True)
        else:  # 引用上一步知识库/文档
            if search_scope_source == 'document':  # 文档
                document_id_list = self.get_reference_content(search_scope_reference)
            else:  # 知识库
                document_id_list = QuerySet(Document).filter(
                    knowledge_id__in=self.get_reference_content(search_scope_reference)
                ).values_list('id', flat=True)

        # 权限过滤
        get_knowledge_list_of_authorized = DatabaseModelManage.get_model('get_knowledge_list_of_authorized')
        chat_user_type = self.workflow_manage.get_body().get('chat_user_type')

        if get_knowledge_list_of_authorized is not None and RoleConstants.CHAT_USER.value.name == chat_user_type:
            # 获取授权的知识库ID列表
            authorized_knowledge_ids = get_knowledge_list_of_authorized(
                self.workflow_manage.get_body().get('chat_user_id'),
                knowledge_id_list
            )

            # 过滤出授权知识库下的文档
            document_id_list = QuerySet(Document).filter(
                id__in=document_id_list,
                knowledge_id__in=authorized_knowledge_ids
            ).values_list('id', flat=True)

        if search_mode == 'auto':  # 通过问题自动检索
            matched_doc_ids = self.handle_auto_tags(document_id_list, question_reference)

            final_document_ids = list(matched_doc_ids)
        else:  # 自定义检索条件
            matched_document_ids = self.handle_custom_tags(
                document_id_list, search_condition_list, search_condition_type
            )

            final_document_ids = list(matched_document_ids)

        # UUID to str
        final_document_ids = [str(doc_id) for doc_id in final_document_ids]
        document_items = QuerySet(Document).filter(id__in=final_document_ids).values()
        final_knowledge_ids = list(set(str(doc['knowledge_id']) for doc in document_items))
        knowledge_items = QuerySet(Knowledge).filter(id__in=final_knowledge_ids).values()

        return NodeResult({
            'document_list': final_document_ids,
            'document_items': list(document_items),
            'knowledge_list': final_knowledge_ids,
            'knowledge_items': list(knowledge_items)
        }, {})

    def handle_auto_tags(self, document_id_list: list, question_reference: list):
        question = self.get_reference_content(question_reference)

        # 使用jieba分词
        keywords = jieba.lcut(question)
        if not keywords:
            return set()

        # 构建OR查询,一次性获取所有匹配的文档
        q_objects = Q()
        for keyword in keywords:
            q_objects |= Q(tag__value__icontains=keyword)

        # 单次数据库查询
        matched_doc_ids = set(
            QuerySet(DocumentTag)
            .filter(document_id__in=document_id_list)
            .filter(q_objects)
            .values_list('document_id', flat=True)
            .distinct()
        )

        return matched_doc_ids

    def handle_custom_tags(self, document_id_list: List, search_condition_list: list, search_condition_type: str):

        if not search_condition_list:
            return set(document_id_list)

        if search_condition_type == 'AND':
            # AND逻辑:使用子查询和聚合
            matched_doc_ids = set(document_id_list)

            for condition in search_condition_list:
                tag_key = condition['key']
                field_value = self.workflow_manage.generate_prompt(condition['value'])
                compare_type = condition['compare']

                if not field_value or field_value == 'None' or len(field_value) == 0:
                    continue

                # 构建查询条件
                if compare_type == 'not_contain':
                    # 反向查询:找出包含该标签的文档,然后排除
                    exclude_docs = set(QuerySet(DocumentTag).filter(
                        document_id__in=matched_doc_ids,
                        tag__key=tag_key,
                        tag__value__icontains=field_value
                    ).values_list('document_id', flat=True).distinct())

                    matched_doc_ids = matched_doc_ids - exclude_docs
                else:
                    if compare_type == 'contain':
                        q_filter = Q(tag__key=tag_key, tag__value__icontains=field_value)
                    elif compare_type == 'eq':
                        q_filter = Q(tag__key=tag_key, tag__value=field_value)
                    else:
                        continue

                    # 单次查询获取符合条件的文档
                    tag_docs = set(QuerySet(DocumentTag).filter(
                        document_id__in=matched_doc_ids
                    ).filter(q_filter).values_list('document_id', flat=True).distinct())

                    matched_doc_ids = matched_doc_ids.intersection(tag_docs)

            return matched_doc_ids

        else:
            # OR逻辑
            matched_docs = set()

            for condition in search_condition_list:
                tag_key = condition['key']
                field_value = self.workflow_manage.generate_prompt(condition['value'])
                compare_type = condition['compare']

                if not field_value or field_value == 'None' or len(field_value) == 0:
                    continue

                if compare_type == 'not_contain':
                    # 反向查询:找出包含该标签的文档,然后用全集减去
                    exclude_docs = set(QuerySet(DocumentTag).filter(
                        document_id__in=document_id_list,
                        tag__key=tag_key,
                        tag__value__icontains=field_value
                    ).values_list('document_id', flat=True).distinct())

                    matched_docs = matched_docs.union(set(document_id_list) - exclude_docs)
                else:
                    if compare_type == 'contain':
                        q_filter = Q(tag__key=tag_key, tag__value__icontains=field_value)
                    elif compare_type == 'eq':
                        q_filter = Q(tag__key=tag_key, tag__value=field_value)
                    else:
                        continue

                    docs = set(QuerySet(DocumentTag).filter(
                        document_id__in=document_id_list
                    ).filter(q_filter).values_list('document_id', flat=True).distinct())

                    matched_docs = matched_docs.union(docs)

            return matched_docs

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            'question': self.context.get('question'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'document_list': self.context.get('document_list'),
            'knowledge_list': self.context.get('knowledge_list'),
            'document_items': self.context.get('document_items'),
            'knowledge_items': self.context.get('knowledge_items'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
