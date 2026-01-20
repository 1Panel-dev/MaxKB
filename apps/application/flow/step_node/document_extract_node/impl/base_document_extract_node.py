# coding=utf-8
import ast
import io

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_extract_node.i_document_extract_node import IDocumentExtractNode
from knowledge.models import File, FileSourceType
from knowledge.serializers.document import split_handles, parse_table_handle_list, FileBufferHandle

splitter = '\n`-----------------------------------`\n'


class BaseDocumentExtractNode(IDocumentExtractNode):
    def save_context(self, details, workflow_manage):
        self.context['content'] = details.get('content')
        self.context['exception_message'] = details.get('err_message')

    def execute(self, document, chat_id=None, **kwargs):
        get_buffer = FileBufferHandle().get_buffer

        self.context['document_list'] = document
        content = []
        if document is None or not isinstance(document, list):
            return NodeResult({'content': '', 'document_list': []}, {})

        # 安全获取 application
        application_id = None
        if (self.workflow_manage and
                self.workflow_manage.work_flow_post_handler and
                self.workflow_manage.work_flow_post_handler.chat_info):
            application_id = self.workflow_manage.work_flow_post_handler.chat_info.application.id
        knowledge_id = self.workflow_params.get('knowledge_id')

        # doc文件中的图片保存
        def save_image(image_list):
            for image in image_list:
                meta = {
                    'debug': False if (application_id or knowledge_id) else True,
                    'chat_id': chat_id,
                    'application_id': str(application_id) if application_id else None,
                    'knowledge_id': str(knowledge_id) if knowledge_id else None,
                    'file_id': str(image.id)
                }
                file_bytes = image.meta.pop('content')
                new_file = File(
                    id=meta['file_id'],
                    file_name=image.file_name,
                    file_size=len(file_bytes),
                    source_type=FileSourceType.APPLICATION.value if meta[
                        'application_id'] else FileSourceType.KNOWLEDGE.value,
                    source_id=meta['application_id'] if meta['application_id'] else meta['knowledge_id'],
                    meta=meta
                )
                if not QuerySet(File).filter(id=new_file.id).exists():
                    new_file.save(file_bytes)

        document_list = []
        for doc in document:
            file = QuerySet(File).filter(id=doc['file_id']).first()
            buffer = io.BytesIO(file.get_bytes())
            buffer.name = doc['name']  # this is the important line

            for split_handle in (parse_table_handle_list + split_handles):
                if split_handle.support(buffer, get_buffer):
                    # 回到文件头
                    buffer.seek(0)
                    file_content = split_handle.get_content(buffer, save_image)
                    content.append('### ' + doc['name'] + '\n' + file_content)
                    document_list.append({'id': str(file.id), 'name': doc['name'], 'content': file_content})
                    break

        return NodeResult({'content': splitter.join(content), 'document_list': document_list}, {})

    def get_details(self, index: int, **kwargs):
        content = self.context.get('content', '').split(splitter)
        # 不保存content全部内容，因为content内容可能会很大
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'content': [file_content[:500] for file_content in content],
            'status': self.status,
            'err_message': self.err_message,
            'document_list': self.context.get('document_list'),
            'enableException': self.node.properties.get('enableException'),
        }
