# coding=utf-8
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.views import Request
from common.auth import TokenAuth, AllTokenAuth
from common.log.log import log
from common.result import result
from knowledge.api.file import FileUploadAPI, FileGetAPI
from oss.serializers.file import FileSerializer, get_url_content


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
    authentication_classes = [AllTokenAuth]
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
    authentication_classes = [AllTokenAuth]

    @extend_schema(
        methods=['GET'],
        summary=_('Get url'),
        description=_('Get url'),
        operation_id=_('Get url'),  # type: ignore
        tags=[_('Chat')]  # type: ignore
    )
    def get(self, request: Request, application_id: str):
        url = request.query_params.get('url')
        result_data = get_url_content(url, application_id)
        return result.success(result_data)
