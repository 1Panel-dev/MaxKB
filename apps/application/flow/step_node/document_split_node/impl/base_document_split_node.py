# coding=utf-8
import io
import mimetypes

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models import QuerySet

from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_split_node.i_document_split_node import IDocumentSplitNode
from knowledge.models import File, FileSourceType
from knowledge.serializers.document import split_handles, FileBufferHandle


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


class BaseDocumentSplitNode(IDocumentSplitNode):
    def save_context(self, details, workflow_manage):
        self.context['content'] = details.get('content')

    def execute(self, files, knowledge_id, split_strategy, paragraph_title_relate_problem_type,
                paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                document_name_relate_problem_type, document_name_relate_problem,
                document_name_relate_problem_reference, limit, patterns, with_filter, **kwargs) -> NodeResult:
        get_buffer = FileBufferHandle().get_buffer
        self.context['file_list'] = files
        self.context['knowledge_id'] = knowledge_id

        paragraph_list = []
        for doc in files:
            file = QuerySet(File).filter(id=doc['file_id']).first()
            file_mem = bytes_to_uploaded_file(file.get_bytes(), file_name=file.file_name)

            for split_handle in split_handles:
                if split_handle.support(file_mem, get_buffer):
                    result = split_handle.handle(file_mem, patterns, with_filter, limit, get_buffer, self.save_image)
                    if isinstance(result, list):
                        for item in result:
                            item['source_file_id'] = file.id
                        paragraph_list = result
                    else:
                        result['source_file_id'] = file.id
                        paragraph_list = [result]

        self.context['paragraph_list'] = paragraph_list


        return NodeResult({'paragraph_list': paragraph_list}, {})

    def save_image(self, image_list):
        if image_list is not None and len(image_list) > 0:
            exist_image_list = [str(i.get('id')) for i in
                                QuerySet(File).filter(id__in=[i.id for i in image_list]).values('id')]
            save_image_list = [image for image in image_list if not exist_image_list.__contains__(str(image.id))]
            save_image_list = list({img.id: img for img in save_image_list}.values())
            # save image
            for file in save_image_list:
                file_bytes = file.meta.pop('content')
                file.meta['knowledge_id'] = self.context.get('knowledge_id')
                file.source_type = FileSourceType.KNOWLEDGE
                file.source_id = self.context.get('knowledge_id')
                file.save(file_bytes)

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'file_list': self.context.get('file_list'),
            'paragraph_list': self.context.get('paragraph_list', []),
        }
