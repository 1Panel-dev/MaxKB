# coding=utf-8
import re
import urllib

import uuid_utils.compat as uuid
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _, gettext
from rest_framework import serializers

from application.models import Application, ChatShareLink, ApplicationAccessToken
from common.auth.common import FileToken
from common.auth.handle.impl.user_token import get_auth
from common.constants.authentication_type import AuthenticationType
from common.database_model_manage.database_model_manage import DatabaseModelManage
from common.exception.app_exception import NotFound404, AppApiException, AppUnauthorizedFailed
from homepage.serializers.homepage import is_workspace_manage, is_extends_workspace_manage, \
    has_extends_workspace_manage_permission, hasPermission
from knowledge.models import File, FileSourceType, Document, Knowledge
from system_manage.models import WorkspaceUserResourcePermission
from system_manage.models.resource_mapping import ResourceMapping, ResourceType
from tools.serializers.tool import UploadedFileField
from users.models import User

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

_PUBLIC_SOURCE_TYPES = (
    FileSourceType.TEMPORARY_120_MINUTE,
    FileSourceType.TEMPORARY_30_MINUTE,
    FileSourceType.TEMPORARY_1_DAY,
    FileSourceType.SYSTEM,
    FileSourceType.TOOL,
)


def _deny():
    raise AppUnauthorizedFailed(403, gettext('No permission to access'))


def auth(file, mk_file_auth):
    # 公共/临时文件无需鉴权
    if file.source_type in _PUBLIC_SOURCE_TYPES:
        return
    # 如果需要访问的数据类型是对话文件,并且数据已经分析出去就直接放行
    if file.source_type == FileSourceType.CHAT:
        if QuerySet(ChatShareLink).filter(chat_id=file.source_id).exists():
            return
    # 非公共文件,直接拒绝
    if mk_file_auth is None:
        _deny()
    token = FileToken.new_instance(mk_file_auth)
    user_type = AuthenticationType(token.type)

    if user_type in (AuthenticationType.CHAT_USER, AuthenticationType.CHAT_ANONYMOUS_USER):
        _auth_chat(file, token, user_type)
    elif user_type == AuthenticationType.SYSTEM_USER:
        _auth_system(file, token.user_id)
    else:
        # 默认拒绝,避免枚举扩展后静默放行
        _deny()


def _auth_chat(file, token, user_type):
    user_id = token.user_id
    if file.source_type == FileSourceType.APPLICATION:
        if not token.application_id == file.source_id:
            _deny()
        else:
            return
    if file.source_type == FileSourceType.CHAT:
        if file.meta.get('user_id') == user_id:
            return
        # 非本人:存在分享链接才允许
        if not QuerySet(ChatShareLink).filter(chat_id=file.source_id).exists():
            _deny()
        # 匿名用户还需满足应用的登录要求
        if user_type == AuthenticationType.CHAT_ANONYMOUS_USER:
            _check_anonymous_login(file.source_id)
        return

    # DOCUMENT / KNOWLEDGE
    if file.source_type == FileSourceType.DOCUMENT:
        knowledge_id = (QuerySet(Document)
                        .filter(id=file.source_id)
                        .values_list('knowledge_id', flat=True)
                        .first())
        if knowledge_id is None:
            _deny()
    elif file.source_type == FileSourceType.KNOWLEDGE:
        knowledge_id = file.source_id
    else:
        _deny()
        return

    if user_type == AuthenticationType.CHAT_ANONYMOUS_USER:
        _check_knowledge_mapped_to_application(token.application_id, knowledge_id)
        return

    get_authorized = DatabaseModelManage.get_model('get_knowledge_list_of_authorized')
    if knowledge_id not in get_authorized(user_id, [knowledge_id]):
        _deny()


def _check_anonymous_login(chat_id):
    access_token = ApplicationAccessToken.objects.filter(
        application__chat__id=chat_id,
        application__chat__is_deleted=False,
    ).first()
    if (access_token and access_token.authentication
            and access_token.authentication_value.get('type') == 'login'):
        _deny()


def _check_knowledge_mapped_to_application(application_id, knowledge_id):
    if application_id is None or knowledge_id is None:
        _deny()
    exists = QuerySet(ResourceMapping).filter(
        source_type=ResourceType.APPLICATION,
        source_id=str(application_id),
        target_type=ResourceType.KNOWLEDGE,
        target_id=str(knowledge_id),
    ).exists()
    if not exists:
        _deny()


def _auth_system(file, user_id):
    user = QuerySet(User).filter(id=user_id).first()
    if not user:
        _deny()
    user_auth = get_auth(user)

    if file.source_type == FileSourceType.CHAT:
        application = QuerySet(Application).filter(chat__id=file.source_id).first()
        if application is None:
            _deny()
        _check_workspace_resource_permission(
            user_auth, user_id,
            workspace_id=application.workspace_id,
            target_id=application.id,
            auth_target_type="APPLICATION",
            read_permission="APPLICATION:READ",
        )
    elif file.source_type == FileSourceType.APPLICATION:
        application = QuerySet(Application).filter(id=file.source_id).first()
        if application is None:
            _deny()
        _check_workspace_resource_permission(
            user_auth, user_id,
            workspace_id=application.workspace_id,
            target_id=application.id,
            auth_target_type="APPLICATION",
            read_permission="APPLICATION:READ",
        )
    elif file.source_type in (FileSourceType.DOCUMENT, FileSourceType.KNOWLEDGE):
        if file.source_type == FileSourceType.DOCUMENT:
            knowledge_id = (QuerySet(Document)
                            .filter(id=file.source_id)
                            .values_list('knowledge_id', flat=True)
                            .first())
        else:
            knowledge_id = file.source_id
        knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first() if knowledge_id else None
        if knowledge is None:
            _deny()
        _check_workspace_resource_permission(
            user_auth, user_id,
            workspace_id=knowledge.workspace_id,
            target_id=knowledge.id,
            auth_target_type="KNOWLEDGE",
            read_permission="KNOWLEDGE:READ",
        )
    else:
        _deny()


def _check_workspace_resource_permission(user_auth, user_id, *, workspace_id,
                                         target_id, auth_target_type, read_permission):
    if is_workspace_manage(user_auth, workspace_id):
        return
    if (is_extends_workspace_manage(user_auth, workspace_id)
            and has_extends_workspace_manage_permission(user_auth, read_permission, workspace_id)):
        return

    permission_list = (["VIEW", "MANAGE", "ROLE"]
                       if hasPermission(user_auth, read_permission)
                       else ["VIEW", "MANAGE"])
    if not QuerySet(WorkspaceUserResourcePermission).filter(
            target=target_id,
            workspace_id=workspace_id,
            user_id=user_id,
            auth_target_type=auth_target_type,
            permission_list__overlap=permission_list).exists():
        _deny()


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

    def upload(self, with_valid=True, user_id=None):
        if with_valid:
            self.is_valid(raise_exception=True)
        meta = self.data.get('meta', None)
        if not meta:
            meta = {'debug': True}
        if user_id:
            meta['user_id'] = user_id
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

        def get(self, mk_file_auth=None, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            file_id = self.data.get('id')
            file = QuerySet(File).filter(id=file_id).first()
            if file is None:
                raise NotFound404(404, _('File not found'))
            auth(file, mk_file_auth)
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
                'Content-Disposition': f'attachment; filename={encoded_filename}'
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
        raise AppApiException(500, _('Application does not exist'))
    if not application.file_upload_enable:
        raise AppApiException(500, _('File upload is not enabled'))
    file_limit = 50 * 1024 * 1024
    if application.file_upload_setting and application.file_upload_setting.get('fileLimit'):
        file_limit = application.file_upload_setting.get('fileLimit') * 1024 * 1024
    try:
        from common.utils.tool_code import ToolExecutor
        response = ToolExecutor().exec_code(
            """
    def get_url_content(url):
        import requests
        requests.packages.urllib3.disable_warnings()
        response = requests.get(url, verify=False, allow_redirects=False)
        content_type = response.headers.get('Content-Type', '')
        if 'text' in content_type or 'json' in content_type:
            content = response.text
        else:
            import base64
            content = base64.b64encode(response.content).decode('utf-8')
        return {
            "status_code": response.status_code,
            "Content-Type": content_type,
            "Content-Length": response.headers.get('Content-Length', 0),
            "content": content,
        }
    """,
            {"url": url}
        )
    except Exception as e:
        raise AppApiException(500, str(e))
    if int(response.get('Content-Length')) > file_limit:
        raise AppApiException(500, _('File size exceeds limit'))
    return {
        'status_code': response.get('status_code'),
        'Content-Type': response.get('Content-Type'),
        'Content-Length': response.get('Content-Length'),
        'content': response.get('content'),
    }
