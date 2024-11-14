# coding=utf-8
from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_extract_node.i_document_extract_node import IDocumentExtractNode
from dataset.models import File


class BaseDocumentExtractNode(IDocumentExtractNode):
    def execute(self, document, **kwargs):
        self.context['document_list'] = document
        content = ''
        spliter = '\n-----------------------------------\n'
        if len(document) > 0:
            for doc in document:
                file = QuerySet(File).filter(id=doc['file_id']).first()
                file_type = doc['name'].split('.')[-1]
                if file_type.lower() in ['txt', 'md', 'csv', 'html']:
                    content += spliter + doc['name'] + '\n' + file.get_byte().tobytes().decode('utf-8')


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
