# coding=utf-8
import io
import mimetypes
from typing import List

from django.core.files.uploadedfile import InMemoryUploadedFile

from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_split_node.i_document_split_node import IDocumentSplitNode
from common.chunk import text_to_chunk
from knowledge.serializers.document import default_split_handle, FileBufferHandle, md_qa_split_handle


def bytes_to_uploaded_file(file_bytes, file_name="file.txt"):
    if file_name.startswith("http"):
        file_name = "file.txt"
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
        self.context['exception_message'] = details.get('err_message')

    def get_reference_content(self, fields: List[str]):
        return self.workflow_manage.get_reference_field(fields[0], fields[1:])

    def execute(self, document_list, knowledge_id, split_strategy, paragraph_title_relate_problem_type,
                paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                document_name_relate_problem_type, document_name_relate_problem,
                document_name_relate_problem_reference, limit, limit_type, limit_reference, chunk_size, chunk_size_type,
                chunk_size_reference, patterns, patterns_type, patterns_reference, with_filter, with_filter_type,
                with_filter_reference, **kwargs) -> NodeResult:
        self.context['knowledge_id'] = knowledge_id
        file_list = self.get_reference_content(document_list)

        # 处理引用类型的参数
        if patterns_type == 'referencing':
            patterns = self.get_reference_content(patterns_reference)
        if limit_type == 'referencing':
            limit = self.get_reference_content(limit_reference)
        if chunk_size_type == 'referencing':
            chunk_size = self.get_reference_content(chunk_size_reference)
        if with_filter_type == 'referencing':
            with_filter = self.get_reference_content(with_filter_reference)

        paragraph_list = []
        for doc in file_list:
            get_buffer = FileBufferHandle().get_buffer

            file_mem = bytes_to_uploaded_file(doc['content'].encode('utf-8'), doc['name'])
            if split_strategy == 'qa':
                result = md_qa_split_handle.handle(file_mem, get_buffer, self._save_image)
            else:
                result = default_split_handle.handle(file_mem, patterns, with_filter, limit, get_buffer,
                                                     self._save_image)
            # 统一处理结果为列表
            results = result if isinstance(result, list) else [result]

            for item in results:
                self._process_split_result(
                    item, knowledge_id, doc.get('id'), doc.get('name'),
                    split_strategy, paragraph_title_relate_problem_type,
                    paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                    document_name_relate_problem_type, document_name_relate_problem,
                    document_name_relate_problem_reference, chunk_size
                )

            paragraph_list += results

        self.context['paragraph_list'] = paragraph_list
        self.context['document_list'] = file_list
        self.context['limit'] = limit
        self.context['chunk_size'] = chunk_size
        self.context['with_filter'] = with_filter
        self.context['patterns'] = patterns
        self.context['split_strategy'] = split_strategy

        return NodeResult({'paragraph_list': paragraph_list}, {})

    def _save_image(self, image_list):
        pass

    def _process_split_result(
            self, item, knowledge_id, source_file_id, file_name,
            split_strategy, paragraph_title_relate_problem_type,
            paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
            document_name_relate_problem_type, document_name_relate_problem,
            document_name_relate_problem_reference, chunk_size
    ):
        """处理文档分割结果"""
        item['meta'] = {
            'knowledge_id': knowledge_id,
            'source_file_id': source_file_id,
            'source_url': file_name,
        }
        if item.get('name', 'file.txt') == 'file.txt':
            item['name'] = file_name
        item['source_file_id'] = source_file_id
        item['paragraphs'] = item.pop('content', item.get('paragraphs', []))

        for paragraph in item['paragraphs']:
            paragraph['problem_list'] = self._generate_problem_list(
                paragraph, file_name,
                split_strategy, paragraph_title_relate_problem_type,
                paragraph_title_relate_problem, paragraph_title_relate_problem_reference,
                document_name_relate_problem_type, document_name_relate_problem,
                document_name_relate_problem_reference
            )
            paragraph['is_active'] = True
            paragraph['chunks'] = text_to_chunk(paragraph['content'], chunk_size)

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

        problem_list = [
            item for p in paragraph.get('problem_list', []) for item in p.get('content', '').split('<br>')
            if item.strip()
        ]

        if split_strategy == 'auto':
            if paragraph_title_relate_problem and paragraph.get('title'):
                problem_list.append(paragraph.get('title'))
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)
        elif split_strategy == 'custom':
            if paragraph_title_relate_problem and paragraph.get('title'):
                problem_list.append(paragraph.get('title'))
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)
        elif split_strategy == 'qa':
            if document_name_relate_problem and document_name:
                problem_list.append(document_name)

        return list(set(problem_list))

    def get_details(self, index: int, **kwargs):
        paragraph_list = self.context.get('paragraph_list', [])
        # 每个文档保留前5个分段
        limited_paragraph_list = []
        for doc in paragraph_list:
            if doc.get('paragraphs'):
                doc_copy = doc.copy()
                doc_copy['paragraphs'] = doc['paragraphs'][:5]
                limited_paragraph_list.append(doc_copy)
            else:
                limited_paragraph_list.append(doc)
        paragraph_list = limited_paragraph_list

        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'paragraph_list': paragraph_list,
            'limit': self.context.get('limit'),
            'chunk_size': self.context.get('chunk_size'),
            'with_filter': self.context.get('with_filter'),
            'patterns': self.context.get('patterns'),
            'split_strategy': self.context.get('split_strategy'),
            'enableException': self.node.properties.get('enableException'),
            # 'document_list': self.context.get('document_list', []),
        }
