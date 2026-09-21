from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import ViewPermission
from common.log.log import log
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.external_retrieval import ExternalServiceSerializer


class ExternalServiceView(APIView):
    authentication_classes = [TokenAuth]

    @has_permissions(
        PermissionConstants.KNOWLEDGE_READ.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_READ.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            compare=CompareConstants.AND,
        ),
    )
    def get(self, request, workspace_id, knowledge_id):
        return result.success(
            ExternalServiceSerializer(
                data={
                    "workspace_id": workspace_id,
                    "knowledge_id": knowledge_id,
                },
                context={"request": request},
            ).get_settings()
        )

    @has_permissions(
        PermissionConstants.KNOWLEDGE_EDIT.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_EDIT.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            compare=CompareConstants.AND,
        ),
    )
    @log(
        menu="Knowledge Base",
        operate="Modify external retrieval service",
        get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get("knowledge_id")),
    )
    def put(self, request, workspace_id, knowledge_id):
        return result.success(
            ExternalServiceSerializer(
                data={
                    "workspace_id": workspace_id,
                    "knowledge_id": knowledge_id,
                },
                context={"request": request},
            ).update_settings(request.data)
        )
