# coding=utf-8
import io
import mimetypes
from typing import List

from django.core.files.uploadedfile import InMemoryUploadedFile

from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_split_node.i_document_split_node import IDocumentSplitNode
from knowledge.serializers.document import default_split_handle, FileBufferHandle


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

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(fields[0], fields[1:])

    def execute(self, document_list, knowledge_id, split_strategy, paragraph_title_relate_problem_type,
                paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                document_name_relate_problem_type, document_name_relate_problem,
                document_name_relate_problem_reference, limit, patterns, with_filter, **kwargs) -> NodeResult:
        self.context['knowledge_id'] = knowledge_id
        file_list = self.workflow_manage.get_reference_field(document_list[0], document_list[1:])
        paragraph_list = []

        for doc in file_list:
            get_buffer = FileBufferHandle().get_buffer

            file_mem = bytes_to_uploaded_file(doc['content'].encode('utf-8'))
            result = default_split_handle.handle(file_mem, patterns, with_filter, limit, get_buffer, self._save_image)
            # 统一处理结果为列表
            results = result if isinstance(result, list) else [result]

            for item in results:
                self._process_split_result(
                    item, knowledge_id, doc.get('id'), doc.get('name'),
                    split_strategy, paragraph_title_relate_problem_type,
                    paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                    document_name_relate_problem_type, document_name_relate_problem,
                    document_name_relate_problem_reference
                )

            paragraph_list += results

        self.context['paragraph_list'] = paragraph_list

        return NodeResult({'paragraph_list': paragraph_list}, {})

    def _save_image(self, image_list):
        pass

    def _process_split_result(
            self, item, knowledge_id, source_file_id, file_name,
            split_strategy, paragraph_title_relate_problem_type,
            paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
            document_name_relate_problem_type, document_name_relate_problem,
            document_name_relate_problem_reference
    ):
        """处理文档分割结果"""
        item['meta'] = {
            'knowledge_id': knowledge_id,
            'source_file_id': source_file_id,
            'source_url': file_name,
        }
        item['name'] = file_name
        item['paragraphs'] = item.pop('content', [])

        for paragraph in item['paragraphs']:
            paragraph['problem_list'] = self._generate_problem_list(
                paragraph, file_name,
                split_strategy, paragraph_title_relate_problem_type,
                paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                document_name_relate_problem_type, document_name_relate_problem,
                document_name_relate_problem_reference
            )
            paragraph['is_active'] = True

    def _generate_problem_list(
            self, paragraph, document_name, split_strategy, paragraph_title_relate_problem_type,
            paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
            document_name_relate_problem_type, document_name_relate_problem,
            document_name_relate_problem_reference
    ):
        if paragraph_title_relate_problem_type == 'referencing':
            paragraph_title_relate_problem = self.get_reference_content(paragraph_title_relate_problem_reference)
        if document_name_relate_problem_type == 'referencing':
            document_name_relate_problem = self.get_reference_content(document_name_relate_problem_reference)

        problem_list = []
        if split_strategy == 'auto':
            if paragraph_title_relate_problem and paragraph.get('title'):
                problem_list.append(paragraph.get('title'))
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)
        elif split_strategy == 'custom':
            if paragraph_title_relate_problem:
                problem_list.extend(paragraph_title_relate_problem)
            if document_name_relate_problem:
                problem_list.extend(document_name_relate_problem)
        elif split_strategy == 'qa':
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)

        return problem_list

    def get_details(self, index: int, **kwargs):
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'paragraph_list': self.context.get('paragraph_list', []),
        }
