# coding=utf-8
import io

from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_extract_node.i_document_extract_node import IDocumentExtractNode
from dataset.models import File
from dataset.serializers.document_serializers import split_handles, parse_table_handle_list, FileBufferHandle


class BaseDocumentExtractNode(IDocumentExtractNode):
    def execute(self, document, **kwargs):
        get_buffer = FileBufferHandle().get_buffer

        self.context['document_list'] = document
        content = ''
        splitter = '\n-----------------------------------\n'
        if document is None:
            return NodeResult({'content': content}, {})

        for doc in document:
            file = QuerySet(File).filter(id=doc['file_id']).first()
            buffer = io.BytesIO(file.get_byte().tobytes())
            buffer.name = doc['name']  # this is the important line

            for split_handle in (parse_table_handle_list + split_handles):
                if split_handle.support(buffer, get_buffer):
                    # 回到文件头
                    buffer.seek(0)
                    file_content = split_handle.get_content(buffer)
                    content += splitter + '## ' + doc['name'] + '\n' + file_content
                    break

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
