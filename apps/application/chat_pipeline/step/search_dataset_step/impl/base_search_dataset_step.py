# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_search_dataset_step.py
    @date：2024/1/10 10:33
    @desc:
"""
from typing import List

from django.db.models import QuerySet

from application.chat_pipeline.step.search_dataset_step.i_search_dataset_step import ISearchDatasetStep
from common.config.embedding_config import VectorStore, EmbeddingModel
from dataset.models import Paragraph


class BaseSearchDatasetStep(ISearchDatasetStep):

    def execute(self, problem_text: str, dataset_id_list: list[str], exclude_document_id_list: list[str],
                exclude_paragraph_id_list: list[str], top_n: int, similarity: float, padding_problem_text: str = None,
                **kwargs) -> List[Paragraph]:
        exec_problem_text = padding_problem_text if padding_problem_text is not None else problem_text
        embedding_model = EmbeddingModel.get_embedding_model()
        embedding_value = embedding_model.embed_query(exec_problem_text)
        vector = VectorStore.get_embedding_vector()
        embedding_list = vector.query(embedding_value, dataset_id_list, exclude_document_id_list,
                                      exclude_paragraph_id_list, True, top_n, similarity)
        if embedding_list is None:
            return []
        return self.list_paragraph([row.get('paragraph_id') for row in embedding_list], vector)

    @staticmethod
    def list_paragraph(paragraph_id_list: List, vector):
        if paragraph_id_list is None or len(paragraph_id_list) == 0:
            return []
        paragraph_list = QuerySet(Paragraph).filter(id__in=paragraph_id_list)
        # 如果向量库中存在脏数据 直接删除
        if len(paragraph_list) != len(paragraph_id_list):
            exist_paragraph_list = [str(row.id) for row in paragraph_list]
            for paragraph_id in paragraph_id_list:
                if not exist_paragraph_list.__contains__(paragraph_id):
                    vector.delete_by_paragraph_id(paragraph_id)
        return paragraph_list

    def get_details(self, manage, **kwargs):
        step_args = self.context['step_args']

        return {
            'step_type': 'search_step',
            'run_time': self.context['run_time'],
            'problem_text': step_args.get(
                'padding_problem_text') if 'padding_problem_text' in step_args else step_args.get('problem_text'),
            'model_name': EmbeddingModel.get_embedding_model().model_name,
            'message_tokens': 0,
            'answer_tokens': 0,
            'cost': 0
        }
