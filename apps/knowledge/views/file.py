# coding=utf-8
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth import TokenAuth
from common.result import result
from knowledge.api.file import FileUploadAPI, FileGetAPI
from knowledge.serializers.file import FileSerializer


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
    def post(self, request: Request):
        return result.success(FileSerializer(data={'file': request.FILES.get('file')}).upload())

    class Operate(APIView):
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
            return FileSerializer.Operate(data={'id': file_id}).get()

        @extend_schema(
            methods=['DELETE'],
            summary=_('Delete file'),
            description=_('Delete file'),
            operation_id=_('Delete file'),  # type: ignore
            parameters=FileGetAPI.get_parameters(),
            responses=FileGetAPI.get_response(),
            tags=[_('File')]  # type: ignore
        )
        def delete(self, request: Request, file_id: str):
            return result.success(FileSerializer.Operate(data={'id': file_id}).delete())
