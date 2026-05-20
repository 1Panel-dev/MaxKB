# coding=utf-8
import io
import requests

import uuid_utils.compat as uuid
from django.db.models import QuerySet

from application.flow.common import WorkflowMode
from application.flow.i_step_node import NodeResult
from application.flow.step_node.document_extract_node.i_document_extract_node import IDocumentExtractNode
from common.utils.common import get_file_name_from_content_disposition, get_file_name_from_url
from common.utils.logger import maxkb_logger
from knowledge.models import File, FileSourceType
from knowledge.serializers.document import split_handles, parse_table_handle_list, FileBufferHandle
from oss.serializers.file import validate_url, SafeHTTPAdapter

splitter = '\n`-----------------------------------`\n'


class BaseDocumentExtractNode(IDocumentExtractNode):
    def save_context(self, details, workflow_manage):
        self.context['content'] = details.get('content')
        self.context['exception_message'] = details.get('err_message')

    def execute(self, document, chat_id=None, **kwargs):
        get_buffer = FileBufferHandle().get_buffer

        self.context['document_list'] = document
        if document is None or not isinstance(document, list):
            return NodeResult({'content': '', 'document_list': []}, {})

        # 安全获取 application
        application_id = None
        tool_id = None
        knowledge_id = None
        if [WorkflowMode.KNOWLEDGE, WorkflowMode.KNOWLEDGE_LOOP].__contains__(self.workflow_manage.flow.workflow_mode):
            knowledge_id = self.workflow_params.get('knowledge_id')
        elif [WorkflowMode.APPLICATION, WorkflowMode.APPLICATION_LOOP].__contains__(
                self.workflow_manage.flow.workflow_mode):
            application_id = self.workflow_manage.work_flow_post_handler.chat_info.application.id
        elif [WorkflowMode.TOOL, WorkflowMode.TOOL_LOOP].__contains__(self.workflow_manage.flow.workflow_mode):
            tool_id = self.workflow_params.get('tool_id')

        # doc文件中的图片保存
        def save_image(image_list):
            for image in image_list:
                meta = {
                    'debug': False if (application_id or knowledge_id or tool_id) else True,
                    'chat_id': chat_id,
                    'application_id': str(application_id) if application_id else None,
                    'knowledge_id': str(knowledge_id) if knowledge_id else None,
                    'tool_id': str(tool_id) if tool_id else None,
                    'file_id': str(image.id)
                }
                file_bytes = image.meta.pop('content')
                new_file = File(
                    id=meta['file_id'],
                    file_name=image.file_name,
                    file_size=len(file_bytes),
                    source_type=FileSourceType.APPLICATION.value if application_id else FileSourceType.KNOWLEDGE.value if knowledge_id else FileSourceType.APPLICATION.value,
                    source_id=application_id or tool_id or knowledge_id,
                    meta=meta
                )
                if not QuerySet(File).filter(id=new_file.id).exists():
                    new_file.save(file_bytes)

        # 从URL下载文件并保存为File对象
        def download_and_save_file(url, file_name=None):
            try:
                # 验证URL安全性
                validated_url = validate_url(url)

                # 创建安全的HTTP会话
                session = requests.Session()
                safe_adapter = SafeHTTPAdapter()
                session.mount('http://', safe_adapter)
                session.mount('https://', safe_adapter)

                try:
                    # 发送GET请求下载文件
                    response = session.get(
                        validated_url,
                        timeout=30,
                        allow_redirects=True
                    )
                    response.raise_for_status()

                    # 获取文件名（如果未提供）
                    if not file_name:
                        # 如果Content-Disposition头中有文件名，优先使用
                        file_name = get_file_name_from_content_disposition(response.headers.get('Content-Disposition', ''))
                        if file_name is None:
                            # 从URL路径中提取文件名
                            file_name = get_file_name_from_url(validated_url, 'downloaded_document')

                    # 获取文件内容
                    file_bytes = response.content

                    # 生成文件ID
                    file_id = uuid.uuid7()

                    # 确定source_type和source_id
                    source_type = FileSourceType.APPLICATION.value if application_id else FileSourceType.KNOWLEDGE.value if knowledge_id else FileSourceType.TOOL.value
                    source_id = application_id or knowledge_id or tool_id

                    # 创建File对象
                    meta = {
                        'debug': False if (application_id or knowledge_id or tool_id) else True,
                        'chat_id': chat_id,
                        'application_id': str(application_id) if application_id else None,
                        'knowledge_id': str(knowledge_id) if knowledge_id else None,
                        'tool_id': str(tool_id) if tool_id else None,
                        'file_id': str(file_id),
                        'source_url': url
                    }

                    new_file = File(
                        id=file_id,
                        file_name=file_name,
                        file_size=len(file_bytes),
                        source_type=source_type,
                        source_id=source_id,
                        meta=meta
                    )

                    # 保存文件到数据库
                    new_file.save(file_bytes)

                    maxkb_logger.info(f'Successfully downloaded and saved file from URL: {url}, file_id: {file_id}')

                    return new_file

                finally:
                    session.close()

            except Exception as e:
                maxkb_logger.error(f'Failed to download document file from URL: {url}, error: {str(e)}')
                raise Exception(f'Failed to download document file: {str(e)}')

        content = []
        document_list = []
        for doc in document:
            # 考虑API调用时，用户传错了格式，抛出异常提示
            if isinstance(doc, str):
                raise ValueError('The "document_list" parameters must be in the format of `[{ "url": "http......" }, ......]`')

            # 如果是文档的 HTTP(s) URL地址，则先下载并保存到file表中
            if not doc.get("file_id") and doc.get("url") and (doc.get("url").startswith("http:") or doc.get("url").startswith("https:")):
                try:
                    # 下载并保存文件
                    file = download_and_save_file(doc["url"], doc.get('name', None))

                    # 更新doc字典，添加file_id
                    doc['file_id'] = str(file.id)
                    if not doc.get('name'):
                        doc['name'] = file.file_name

                    maxkb_logger.info(f'Downloaded file from URL and assigned file_id: {doc["file_id"]}')
                except Exception as e:
                    maxkb_logger.error(f'Error processing document URL: {doc.get("url")}, error: {str(e)}')
                    raise e
            elif doc.get("file_id"):
                file = QuerySet(File).filter(id=doc['file_id']).first()
            else:
                raise ValueError('Please provide a valid document file ID or URL')

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
