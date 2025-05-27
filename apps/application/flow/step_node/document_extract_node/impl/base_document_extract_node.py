# coding=utf-8
import io
import mimetypes

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_extract_node.i_document_extract_node import IDocumentExtractNode
from dataset.models import File
from dataset.serializers.document_serializers import split_handles, parse_table_handle_list, FileBufferHandle
from dataset.serializers.file_serializers import FileSerializer


def bytes_to_uploaded_file(file_bytes, file_name="file.txt"):
    content_type, _ = mimetypes.guess_type(file_name)
    if content_type is None:
        # 如果未能识别，设置为默认的二进制文件类型
        content_type = "application/octet-stream"
    # 创建一个内存中的字节流对象
    file_stream = io.BytesIO(file_bytes)

    # 获取文件大小
    file_size = len(file_bytes)

    # 创建 InMemoryUploadedFile 对象
    uploaded_file = InMemoryUploadedFile(
        file=file_stream,
        field_name=None,
        name=file_name,
        content_type=content_type,
        size=file_size,
        charset=None,
    )
    return uploaded_file


splitter = '\n`-----------------------------------`\n'

class BaseDocumentExtractNode(IDocumentExtractNode):
    def save_context(self, details, workflow_manage):
        self.context['content'] = details.get('content')


    def execute(self, document, chat_id, **kwargs):
        get_buffer = FileBufferHandle().get_buffer

        self.context['document_list'] = document
        content = []
        if document is None or not isinstance(document, list):
            return NodeResult({'content': ''}, {})

        application = self.workflow_manage.work_flow_post_handler.chat_info.application

        # doc文件中的图片保存
        def save_image(image_list):
            for image in image_list:
                meta = {
                    'debug': False if application.id else True,
                    'chat_id': chat_id,
                    'application_id': str(application.id) if application.id else None,
                    'file_id': str(image.id)
                }
                file = bytes_to_uploaded_file(image.image, image.image_name)
                FileSerializer(data={'file': file, 'meta': meta}).upload()

        for doc in document:
            file = QuerySet(File).filter(id=doc['file_id']).first()
            buffer = io.BytesIO(file.get_byte().tobytes())
            buffer.name = doc['name']  # this is the important line

            for split_handle in (parse_table_handle_list + split_handles):
                if split_handle.support(buffer, get_buffer):
                    # 回到文件头
                    buffer.seek(0)
                    file_content = split_handle.get_content(buffer, save_image)
                    content.append('### ' + doc['name'] + '\n' + file_content)
                    break

        return NodeResult({'content': splitter.join(content)}, {})

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
            'document_list': self.context.get('document_list')
        }
