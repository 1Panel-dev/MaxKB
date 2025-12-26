# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： resource_mapping.py
    @date：2025/12/25 15:28
    @desc:
"""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from system_manage.api.resource_mapping import ResourceMappingAPI
from system_manage.serializers.resource_mapping_serializers import ResourceMappingSerializer


class ResourceMappingView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=['GET'],
        description=_('Retrieve the pagination list of resource relationships'),
        operation_id=_('Retrieve the pagination list of resource relationships'),  # type: ignore
        responses=ResourceMappingAPI.get_response(),
        parameters=ResourceMappingAPI.get_parameters(),
        tags=[_('Resources mapping')]  # type: ignore
    )
    def get(self, request: Request, workspace_id: str, resource: str, resource_id: str, current_page, page_size):
        return result.success(ResourceMappingSerializer({
            'resource': resource,
            'resource_id': resource_id,
            'resource_name': request.query_params.get('resource_name')
        }).page(current_page, page_size))
