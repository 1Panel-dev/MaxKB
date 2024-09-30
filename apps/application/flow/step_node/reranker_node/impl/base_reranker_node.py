# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： base_reranker_node.py
    @date：2024/9/4 11:41
    @desc:
"""
from typing import List

from langchain_core.documents import Document

from application.flow.i_step_node import NodeResult
from application.flow.step_node.reranker_node.i_reranker_node import IRerankerNode
from setting.models_provider.tools import get_model_instance_by_model_user_id


def merge_reranker_list(reranker_list, result=None):
    if result is None:
        result = []
    for document in reranker_list:
        if isinstance(document, list):
            merge_reranker_list(document, result)
        elif isinstance(document, dict):
            content = document.get('title', '') + document.get('content', '')
            result.append(str(document) if len(content) == 0 else content)
        else:
            result.append(str(document))
    return result


def filter_result(document_list: List[Document], max_paragraph_char_number, top_n, similarity):
    use_len = 0
    result = []
    for index in range(len(document_list)):
        document = document_list[index]
        if use_len >= max_paragraph_char_number or index >= top_n or document.metadata.get(
                'relevance_score') < similarity:
            break
        content = document.page_content[0:max_paragraph_char_number - use_len]
        use_len = use_len + len(content)
        result.append({'page_content': content, 'metadata': document.metadata})
    return result


class BaseRerankerNode(IRerankerNode):
    def execute(self, question, reranker_setting, reranker_list, reranker_model_id,
                **kwargs) -> NodeResult:
        documents = merge_reranker_list(reranker_list)
        top_n = reranker_setting.get('top_n', 3)
        self.context['document_list'] = documents
        self.context['question'] = question
        reranker_model = get_model_instance_by_model_user_id(reranker_model_id,
                                                             self.flow_params_serializer.data.get('user_id'),
                                                             top_n=top_n)
        result = reranker_model.compress_documents(
            [Document(page_content=document) for document in documents if document is not None and len(document) > 0],
            question)
        similarity = reranker_setting.get('similarity', 0.6)
        max_paragraph_char_number = reranker_setting.get('max_paragraph_char_number', 5000)
        r = filter_result(result, max_paragraph_char_number, top_n, similarity)
        return NodeResult({'result_list': r, 'result': ''.join([item.get('page_content') for item in r])}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'document_list': self.context.get('document_list'),
            "question": self.context.get('question'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'reranker_setting': self.node_params_serializer.data.get('reranker_setting'),
            'result_list': self.context.get('result_list'),
            'result': self.context.get('result'),
            'status': self.status,
            'err_message': self.err_message
        }
