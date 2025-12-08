from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants, ViewPermission, CompareConstants
from common.log.log import log
from common.result import result
from knowledge.api.tag import TagCreateAPI, TagDeleteAPI, TagEditAPI
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.tag import TagSerializers


class KnowledgeTagView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        summary=_("Create Knowledge Tag"),
        description=_("Create a new knowledge tag"),
        parameters=TagCreateAPI.get_parameters(),
        request=TagCreateAPI.get_request(),
        responses=TagCreateAPI.get_response(),
        tags=[_('Knowledge Base/Tag')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_TAG_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_TAG_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(
        menu='tag', operate="Create a knowledge tag",
        get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id'))
    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(TagSerializers.Create(
            data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'tags': request.data}
        ).insert())

    @extend_schema(
        summary=_("Get Knowledge Tag"),
        description=_("Get knowledge tag"),
        parameters=TagCreateAPI.get_parameters(),
        request=TagCreateAPI.get_request(),
        responses=TagCreateAPI.get_response(),
        tags=[_('Knowledge Base/Tag')]  # type: ignore
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_TAG_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_TAG_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission([RoleConstants.USER.get_workspace_role()],
                       [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
    )
    @log(
        menu='tag', operate="Create a knowledge tag",
        get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id'))
    )
    def get(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(TagSerializers.Query(data={
            'workspace_id': workspace_id,
            'knowledge_id': knowledge_id,
            'name': request.query_params.get('name')
        }).list())

    class Operate(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_("Update Knowledge Tag"),
            description=_("Update a knowledge tag"),
            parameters=TagEditAPI.get_parameters(),
            request=TagEditAPI.get_request(),
            responses=TagEditAPI.get_response(),
            tags=[_('Knowledge Base/Tag')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TAG_EDIT.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TAG_EDIT.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='tag', operate="Update a knowledge tag",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id'))
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str, tag_id: str):
            return result.success(TagSerializers.Operate(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'tag_id': tag_id}
            ).edit(request.data))

    class Delete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_("Delete Knowledge Tag"),
            description=_("Delete a knowledge tag"),
            parameters=TagDeleteAPI.get_parameters(),
            request=TagDeleteAPI.get_request(),
            responses=TagDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Tag')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TAG_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TAG_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='tag', operate="Delete a knowledge tag",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id'))
        )
        def delete(self, request: Request, workspace_id: str, knowledge_id: str, tag_id: str, delete_type: str):
            return result.success(TagSerializers.Operate(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'tag_id': tag_id}
            ).delete(delete_type))

    class BatchDelete(APIView):
        authentication_classes = [TokenAuth]

        @extend_schema(
            summary=_("Batch Delete Knowledge Tag"),
            description=_("Batch Delete a knowledge tag"),
            parameters=TagDeleteAPI.get_parameters(),
            request=TagDeleteAPI.get_request(),
            responses=TagDeleteAPI.get_response(),
            tags=[_('Knowledge Base/Tag')]  # type: ignore
        )
        @has_permissions(
            PermissionConstants.KNOWLEDGE_TAG_DELETE.get_workspace_knowledge_permission(),
            PermissionConstants.KNOWLEDGE_TAG_DELETE.get_workspace_permission_workspace_manage_role(),
            RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
            ViewPermission([RoleConstants.USER.get_workspace_role()],
                           [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
        )
        @log(
            menu='tag', operate="Batch Delete knowledge tag",
            get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get('knowledge_id'))
        )
        def put(self, request: Request, workspace_id: str, knowledge_id: str):
            return result.success(TagSerializers.BatchDelete(
                data={'workspace_id': workspace_id, 'knowledge_id': knowledge_id, 'tag_ids': request.data}
            ).batch_delete())
