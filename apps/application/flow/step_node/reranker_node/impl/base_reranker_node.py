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
from models_provider.tools import get_model_instance_by_model_workspace_id


def merge_reranker_list(reranker_list, result=None):
    if result is None:
        result = []
    for document in reranker_list:
        if isinstance(document, list):
            merge_reranker_list(document, result)
        elif isinstance(document, dict):
            content = document.get('title', '') + document.get('content', '')
            title = document.get("title")
            result.append(
                Document(page_content=str(document) if len(content) == 0 else content,
                         metadata={'title': title, **document}))
        else:
            result.append(Document(page_content=str(document), metadata={}))
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


def reset_result_list(result_list: List[Document], document_list: List[Document]):
    r = []
    document_list = document_list.copy()
    for result in result_list:
        filter_result_list = [document for document in document_list if document.page_content == result.page_content]
        if len(filter_result_list) > 0:
            item = filter_result_list[0]
            document_list.remove(item)
            r.append(Document(page_content=item.page_content,
                              metadata={**item.metadata, 'relevance_score': result.metadata.get('relevance_score')}))
        else:
            r.append(result)
    return r


def get_none_result(question):
    return NodeResult(
        {'document_list': [], 'question': question,
         'result_list': [], 'result': ''}, {})


def reset_metadata(metadata):
    meta = metadata.get('meta')
    if isinstance(metadata.get('meta'), dict):
        if not meta.get('allow_download', False):
            metadata['meta'] = {'allow_download': False}
    return metadata


class BaseRerankerNode(IRerankerNode):
    def save_context(self, details, workflow_manage):
        self.context['document_list'] = details.get('document_list', [])
        self.context['question'] = details.get('question')
        self.context['run_time'] = details.get('run_time')
        self.context['result_list'] = details.get('result_list')
        self.context['result'] = details.get('result')
        self.context['exception_message'] = details.get('err_message')

    def execute(self, question, reranker_setting, reranker_list, reranker_model_id, show_knowledge,
                **kwargs) -> NodeResult:
        self.context['show_knowledge'] = show_knowledge
        documents = merge_reranker_list(reranker_list)
        documents = [d for d in documents if d.page_content and len(d.page_content) > 0]
        if len(documents) == 0:
            return get_none_result(question)
        top_n = reranker_setting.get('top_n', 3)
        self.context['document_list'] = [
            {'page_content': document.page_content, 'metadata': reset_metadata(document.metadata)} for
            document in documents]
        self.context['question'] = question
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        reranker_model = get_model_instance_by_model_workspace_id(reranker_model_id,
                                                                  workspace_id,
                                                                  top_n=top_n)
        result = reranker_model.compress_documents(
            documents,
            question)
        similarity = reranker_setting.get('similarity', 0.6)
        max_paragraph_char_number = reranker_setting.get('max_paragraph_char_number', 5000)
        result = reset_result_list(result, documents)
        r = filter_result(result, max_paragraph_char_number, top_n, similarity)
        return NodeResult({'result_list': r, 'result': ''.join([item.get('page_content') for item in r])}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'show_knowledge': self.context.get('show_knowledge'),
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
            'err_message': self.err_message,
            'enableException': self.node.properties.get('enableException'),
        }
