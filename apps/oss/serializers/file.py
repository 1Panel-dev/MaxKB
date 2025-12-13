# coding=utf-8
import base64
import ipaddress
import re
import socket
import urllib
from urllib.parse import urlparse

import requests
import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from application.models import Application
from common.exception.app_exception import NotFound404, AppApiException
from knowledge.models import File, FileSourceType
from tools.serializers.tool import UploadedFileField

mime_types = {
    "html": "text/html", "htm": "text/html", "shtml": "text/html", "css": "text/css", "xml": "text/xml",
    "gif": "image/gif", "jpeg": "image/jpeg", "jpg": "image/jpeg", "js": "application/javascript",
    "atom": "application/atom+xml", "rss": "application/rss+xml", "mml": "text/mathml", "txt": "text/plain",
    "jad": "text/vnd.sun.j2me.app-descriptor", "wml": "text/vnd.wap.wml", "htc": "text/x-component",
    "avif": "image/avif", "png": "image/png", "svg": "image/svg+xml", "svgz": "image/svg+xml",
    "tif": "image/tiff", "tiff": "image/tiff", "wbmp": "image/vnd.wap.wbmp", "webp": "image/webp",
    "ico": "image/x-icon", "jng": "image/x-jng", "bmp": "image/x-ms-bmp", "woff": "font/woff",
    "woff2": "font/woff2", "jar": "application/java-archive", "war": "application/java-archive",
    "ear": "application/java-archive", "json": "application/json", "hqx": "application/mac-binhex40",
    "doc": "application/msword", "pdf": "application/pdf", "ps": "application/postscript",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "eps": "application/postscript", "ai": "application/postscript", "rtf": "application/rtf",
    "m3u8": "application/vnd.apple.mpegurl", "kml": "application/vnd.google-earth.kml+xml",
    "kmz": "application/vnd.google-earth.kmz", "xls": "application/vnd.ms-excel",
    "eot": "application/vnd.ms-fontobject", "ppt": "application/vnd.ms-powerpoint",
    "odg": "application/vnd.oasis.opendocument.graphics",
    "odp": "application/vnd.oasis.opendocument.presentation",
    "ods": "application/vnd.oasis.opendocument.spreadsheet", "odt": "application/vnd.oasis.opendocument.text",
    "wmlc": "application/vnd.wap.wmlc", "wasm": "application/wasm", "7z": "application/x-7z-compressed",
    "cco": "application/x-cocoa", "jardiff": "application/x-java-archive-diff",
    "jnlp": "application/x-java-jnlp-file", "run": "application/x-makeself", "pl": "application/x-perl",
    "pm": "application/x-perl", "prc": "application/x-pilot", "pdb": "application/x-pilot",
    "rar": "application/x-rar-compressed", "rpm": "application/x-redhat-package-manager",
    "sea": "application/x-sea", "swf": "application/x-shockwave-flash", "sit": "application/x-stuffit",
    "tcl": "application/x-tcl", "tk": "application/x-tcl", "der": "application/x-x509-ca-cert",
    "pem": "application/x-x509-ca-cert", "crt": "application/x-x509-ca-cert",
    "xpi": "application/x-xpinstall", "xhtml": "application/xhtml+xml", "xspf": "application/xspf+xml",
    "zip": "application/zip", "bin": "application/octet-stream", "exe": "application/octet-stream",
    "dll": "application/octet-stream", "deb": "application/octet-stream", "dmg": "application/octet-stream",
    "iso": "application/octet-stream", "img": "application/octet-stream", "msi": "application/octet-stream",
    "msp": "application/octet-stream", "msm": "application/octet-stream", "mid": "audio/midi",
    "midi": "audio/midi", "kar": "audio/midi", "mp3": "audio/mp3", "ogg": "audio/ogg", "m4a": "audio/x-m4a",
    "ra": "audio/x-realaudio", "3gpp": "video/3gpp", "3gp": "video/3gpp", "ts": "video/mp2t",
    "mp4": "video/mp4", "mpeg": "video/mpeg", "mpg": "video/mpeg", "mov": "video/quicktime",
    "webm": "video/webm", "flv": "video/x-flv", "m4v": "video/x-m4v", "mng": "video/x-mng",
    "asx": "video/x-ms-asf", "asf": "video/x-ms-asf", "wmv": "video/x-ms-wmv", "avi": "video/x-msvideo",
    "wav": "audio/wav", "flac": "audio/flac", "aac": "audio/aac", "opus": "audio/opus",
    "csv": "text/csv", "tsv": "text/tab-separated-values", "ics": "text/calendar",
}

# 如果是音频文件并且有range请求，处理部分内容
audio_types = ['mp3', 'wav', 'ogg', 'flac', 'aac', 'opus', 'm4a']


class FileSerializer(serializers.Serializer):
    file = UploadedFileField(required=True, label=_('file'))
    meta = serializers.JSONField(required=False, allow_null=True)
    source_id = serializers.CharField(
        required=False, allow_null=True, label=_('source id'), default=FileSourceType.TEMPORARY_120_MINUTE.value
    )
    source_type = serializers.ChoiceField(
        choices=FileSourceType.choices, required=False, allow_null=True, label=_('source type'),
        default=FileSourceType.TEMPORARY_120_MINUTE
    )

    def upload(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        meta = self.data.get('meta', None)
        if not meta:
            meta = {'debug': True}
        file_id = meta.get('file_id', uuid.uuid7())
        file = File(
            id=file_id,
            file_name=self.data.get('file').name,
            meta=meta,
            source_id=self.data.get('source_id') or FileSourceType.TEMPORARY_120_MINUTE.value,
            source_type=self.data.get('source_type') or FileSourceType.TEMPORARY_120_MINUTE
        )
        file.save(self.data.get('file').read())
        return f'./oss/file/{file_id}'

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True)
        http_range = serializers.CharField(
            required=False, allow_blank=True, allow_null=True, label=_('HTTP Range'),
            help_text=_('HTTP Range header for partial content requests, e.g., "bytes=0-1023"')
        )

        def get(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            file_id = self.data.get('id')
            file = QuerySet(File).filter(id=file_id).first()
            if file is None:
                raise NotFound404(404, _('File not found'))
            file_type = file.file_name.split(".")[-1].lower()
            content_type = mime_types.get(file_type, 'application/octet-stream')
            encoded_filename = urllib.parse.quote(file.file_name)
            # 获取文件内容
            file_bytes = file.get_bytes()
            file_size = len(file_bytes)

            response = None
            if file_type in audio_types and self.data.get('http_range'):
                response = self.handle_audio(file_size, file_bytes, content_type, encoded_filename)
            if response:
                return response

            # 对于非范围请求或其他类型文件，返回完整内容
            headers = {
                'Content-Type': content_type,
                'Content-Disposition': f'{"inline" if file_type == "pdf" else "attachment"}; filename={encoded_filename}'
            }
            return HttpResponse(
                file_bytes,
                status=200,
                headers=headers
            )

        def handle_audio(self, file_size, file_bytes, content_type, encoded_filename):

            # 解析range请求 (格式如 "bytes=0-1023")
            range_match = re.match(r'bytes=(\d+)-(\d*)', self.data.get('http_range', ''))
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

                # 确保范围合法
                end = min(end, file_size - 1)
                length = end - start + 1

                # 创建部分响应
                response = HttpResponse(
                    file_bytes[start:start + length],
                    status=206,
                    content_type=content_type
                )

                # 设置部分内容响应头
                response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
                response['Accept-Ranges'] = 'bytes'
                response['Content-Length'] = str(length)
                response['Content-Disposition'] = f'inline; filename={encoded_filename}'
                return response

        def delete(self):
            self.is_valid(raise_exception=True)
            file_id = self.data.get('id')
            file = QuerySet(File).filter(id=file_id).first()
            if file is not None:
                file.delete()
            return True


def get_url_content(url, application_id: str):
    application = Application.objects.filter(id=application_id).first()
    if application is None:
        return AppApiException(500, _('Application does not exist'))
    if not application.file_upload_enable:
        return AppApiException(500, _('File upload is not enabled'))
    file_limit = 50 * 1024 * 1024
    if application.file_upload_setting and application.file_upload_setting.get('fileLimit'):
        file_limit = application.file_upload_setting.get('fileLimit') * 1024 * 1024
    parsed = validate_url(url)

    response = requests.get(
        url,
        timeout=3,
        allow_redirects=False
    )
    final_host = urlparse(response.url).hostname
    if is_private_ip(final_host):
        raise ValueError("Blocked unsafe redirect to internal host")
    # 判断文件大小
    if int(response.headers.get('Content-Length', 0)) > file_limit:
        raise AppApiException(500, _('File size exceeds limit'))
    # 返回状态码 响应内容大小  响应的contenttype 还有字节流
    content_type = response.headers.get('Content-Type', '')
    # 根据内容类型决定如何处理
    if 'text' in content_type or 'json' in content_type:
        content = response.text
    else:
        # 二进制内容使用Base64编码
        content = base64.b64encode(response.content).decode('utf-8')

    return {
        'status_code': response.status_code,
        'Content-Length': response.headers.get('Content-Length', 0),
        'Content-Type': content_type,
        'content': content,
    }


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
    # 域名不能为空
    if not host:
        raise ValueError("Invalid URL")

    # 禁止访问内部、保留、环回、云 metadata
    if is_private_ip(host):
        raise ValueError("Access to internal IP addresses is blocked")

    return parsed
