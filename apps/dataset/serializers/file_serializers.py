# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： image_serializers.py
    @date：2024/4/22 16:36
    @desc:
"""
import uuid

from django.db.models import QuerySet
from django.http import HttpResponse
from rest_framework import serializers

from common.exception.app_exception import NotFound404
from common.field.common import UploadedFileField
from common.util.field_message import ErrMessage
from dataset.models import File

mime_types = {"html": "text/html", "htm": "text/html", "shtml": "text/html", "css": "text/css", "xml": "text/xml",
              "gif": "image/gif", "jpeg": "image/jpeg", "jpg": "image/jpeg", "js": "application/javascript",
              "atom": "application/atom+xml", "rss": "application/rss+xml", "mml": "text/mathml", "txt": "text/plain",
              "jad": "text/vnd.sun.j2me.app-descriptor", "wml": "text/vnd.wap.wml", "htc": "text/x-component",
              "avif": "image/avif", "png": "image/png", "svg": "image/svg+xml", "svgz": "image/svg+xml",
              "tif": "image/tiff", "tiff": "image/tiff", "wbmp": "image/vnd.wap.wbmp", "webp": "image/webp",
              "ico": "image/x-icon", "jng": "image/x-jng", "bmp": "image/x-ms-bmp", "woff": "font/woff",
              "woff2": "font/woff2", "jar": "application/java-archive", "war": "application/java-archive",
              "ear": "application/java-archive", "json": "application/json", "hqx": "application/mac-binhex40",
              "doc": "application/msword", "pdf": "application/pdf", "ps": "application/postscript",
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
              "midi": "audio/midi", "kar": "audio/midi", "mp3": "audio/mpeg", "ogg": "audio/ogg", "m4a": "audio/x-m4a",
              "ra": "audio/x-realaudio", "3gpp": "video/3gpp", "3gp": "video/3gpp", "ts": "video/mp2t",
              "mp4": "video/mp4", "mpeg": "video/mpeg", "mpg": "video/mpeg", "mov": "video/quicktime",
              "webm": "video/webm", "flv": "video/x-flv", "m4v": "video/x-m4v", "mng": "video/x-mng",
              "asx": "video/x-ms-asf", "asf": "video/x-ms-asf", "wmv": "video/x-ms-wmv", "avi": "video/x-msvideo"}


class FileSerializer(serializers.Serializer):
    file = UploadedFileField(required=True, error_messages=ErrMessage.image("文件"))

    def upload(self, with_valid=True):
        if with_valid:
            self.is_valid(raise_exception=True)
        file_id = uuid.uuid1()
        file = File(id=file_id, file_name=self.data.get('file').name)
        file.save(self.data.get('file').read())
        return f'/api/file/{file_id}'

    class Operate(serializers.Serializer):
        id = serializers.UUIDField(required=True)

        def get(self, with_valid=True):
            if with_valid:
                self.is_valid(raise_exception=True)
            file_id = self.data.get('id')
            file = QuerySet(File).filter(id=file_id).first()
            if file is None:
                raise NotFound404(404, "不存在的文件")
            return HttpResponse(file.get_byte(), status=200,
                                headers={'Content-Type': mime_types.get(file.file_name.split(".")[-1], 'text/plain')})
