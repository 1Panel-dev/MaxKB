# coding=utf-8
from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_extract_node.i_document_extract_node import IDocumentExtractNode


class BaseDocumentExtractNode(IDocumentExtractNode):
    def execute(self, document, **kwargs):
        self.context['document_list'] = document
        content = ''
        if len(document) > 0:
            for doc in document:
                content += doc['name']
                content += '\n-----------------------------------\n'
        return NodeResult({'content': content}, {})

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'content': self.context.get('content'),
            'status': self.status,
            'err_message': self.err_message,
            'document_list': self.context.get('document_list')
        }
