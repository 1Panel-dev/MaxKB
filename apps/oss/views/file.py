# coding=utf-8
import base64
import ipaddress
import socket
from urllib.parse import urlparse

import requests
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth
from common.log.log import log
from common.result import result
from knowledge.api.file import FileUploadAPI, FileGetAPI
from oss.serializers.file import FileSerializer


class FileRetrievalView(APIView):
    @extend_schema(
        methods=['GET'],
        summary=_('Get file'),
        description=_('Get file'),
        operation_id=_('Get file'),  # type: ignore
        parameters=FileGetAPI.get_parameters(),
        responses=FileGetAPI.get_response(),
        tags=[_('File')]  # type: ignore
    )
    def get(self, request: Request, file_id: str):
        return FileSerializer.Operate(data={
            'id': file_id,
            'http_range': request.headers.get('Range', ''),
        }).get()


class FileView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @extend_schema(
        methods=['POST'],
        summary=_('Upload file'),
        description=_('Upload file'),
        operation_id=_('Upload file'),  # type: ignore
        parameters=FileUploadAPI.get_parameters(),
        request=FileUploadAPI.get_request(),
        responses=FileUploadAPI.get_response(),
        tags=[_('File')]  # type: ignore
    )
    @log(menu='file', operate='Upload file')
    def post(self, request: Request):
        return result.success(FileSerializer(data={
            'file': request.FILES.get('file'),
            'source_id': request.data.get('source_id'),
            'source_type': request.data.get('source_type'),
        }).upload())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            methods=['DELETE'],
            summary=_('Delete file'),
            description=_('Delete file'),
            operation_id=_('Delete file'),  # type: ignore
            parameters=FileGetAPI.get_parameters(),
            responses=FileGetAPI.get_response(),
            tags=[_('File')]  # type: ignore
        )
        @log(menu='file', operate='Delete file')
        def delete(self, request: Request, file_id: str):
            return result.success(FileSerializer.Operate(data={'id': file_id}).delete())


class GetUrlView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        summary=_('Get url'),
        description=_('Get url'),
        operation_id=_('Get url'),  # type: ignore
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request):
        url = request.query_params.get('url')
        parsed = validate_url(url)

        response = requests.get(
            url,
            timeout=3,
            allow_redirects=False
        )
        final_host = urlparse(response.url).hostname
        if is_private_ip(final_host):
            raise ValueError("Blocked unsafe redirect to internal host")

        # 返回状态码 响应内容大小  响应的contenttype 还有字节流
        content_type = response.headers.get('Content-Type', '')
        # 根据内容类型决定如何处理
        if 'text' in content_type or 'json' in content_type:
            content = response.text
        else:
            # 二进制内容使用Base64编码
            content = base64.b64encode(response.content).decode('utf-8')

        return result.success({
            'status_code': response.status_code,
            'Content-Length': response.headers.get('Content-Length', 0),
            'Content-Type': content_type,
            'content': content,
        })


def is_private_ip(host: str) -> bool:
    """检测 IP 是否属于内网、环回、云 metadata 的危险地址"""
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(host))
        return (
                ip.is_private or
                ip.is_loopback or
                ip.is_reserved or
                ip.is_link_local or
                ip.is_multicast
        )
    except Exception:
        return True


def validate_url(url: str):
    """验证 URL 是否安全"""
    if not url:
        raise ValueError("URL is required")

    parsed = urlparse(url)

    # 仅允许 http / https
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http and https are allowed")

    host = parsed.hostname
    path = parsed.path

    # 域名不能为空
    if not host:
        raise ValueError("Invalid URL")

    # 禁止访问内部、保留、环回、云 metadata
    if is_private_ip(host):
        raise ValueError("Access to internal IP addresses is blocked")

    return parsed
