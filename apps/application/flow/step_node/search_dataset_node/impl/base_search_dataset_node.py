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

from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.search_dataset_node.i_search_dataset_node import ISearchDatasetStepNode
from common.config.embedding_config import EmbeddingModel, VectorStore
from common.db.search import native_search
from common.util.file_util import get_file_content
from dataset.models import Document, Paragraph
from embedding.models import SearchMode
from smartdoc.conf import PROJECT_DIR


class BaseSearchDatasetNode(ISearchDatasetStepNode):
    def execute(self, dataset_id_list, dataset_setting, question,
                exclude_paragraph_id_list=None,
                **kwargs) -> NodeResult:
        self.context['question'] = question
        embedding_model = EmbeddingModel.get_embedding_model()
        embedding_value = embedding_model.embed_query(question)
        vector = VectorStore.get_embedding_vector()
        exclude_document_id_list = [str(document.id) for document in
                                    QuerySet(Document).filter(
                                        dataset_id__in=dataset_id_list,
                                        is_active=False)]
        embedding_list = vector.query(question, embedding_value, dataset_id_list, exclude_document_id_list,
                                      exclude_paragraph_id_list, True, dataset_setting.get('top_n'),
                                      dataset_setting.get('similarity'), SearchMode(dataset_setting.get('search_mode')))
        if embedding_list is None:
            return NodeResult({'paragraph_list': [], 'is_hit_handling_method': []}, {})
        paragraph_list = self.list_paragraph(embedding_list, vector)
        result = [self.reset_paragraph(paragraph, embedding_list) for paragraph in paragraph_list]
        return NodeResult({'paragraph_list': result,
                           'is_hit_handling_method_list': [row for row in result if row.get('is_hit_handling_method')],
                           'data': '\n'.join([paragraph.get('content') for paragraph in paragraph_list]),
                           'directly_return': '\n'.join([paragraph.get('content') for paragraph in result if
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
                    'directly_return_similarity') and paragraph.get('hit_handling_method') == 'directly_return'
            }

    @staticmethod
    def list_paragraph(embedding_list: List, vector):
        paragraph_id_list = [row.get('paragraph_id') for row in embedding_list]
        if paragraph_id_list is None or len(paragraph_id_list) == 0:
            return []
        paragraph_list = native_search(QuerySet(Paragraph).filter(id__in=paragraph_id_list),
                                       get_file_content(
                                           os.path.join(PROJECT_DIR, "apps", "application", 'sql',
                                                        'list_dataset_paragraph_by_paragraph_id.sql')),
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
            'question': self.context.get('question'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'paragraph_list': self.context.get('paragraph_list'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message
        }
