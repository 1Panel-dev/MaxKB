from knowledge.permissions import knowledge_permission
from rest_framework.views import APIView

from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.permission_constants import PermissionConstants
from common.log.log import log
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.external_retrieval import ExternalServiceSerializer


class ExternalServiceView(APIView):
    authentication_classes = [TokenAuth]

    @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_EXTERNAL_SERVICE_READ))
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

    @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_EXTERNAL_SERVICE_EDIT))
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


class KnowledgeMcpConfigView(APIView):
    authentication_classes = [TokenAuth]

    @has_permissions(knowledge_permission(PermissionConstants.KNOWLEDGE_MCP_CONFIG))
    def get(self, request, workspace_id, knowledge_id):
        config = ExternalServiceSerializer(
            data={"workspace_id": workspace_id, "knowledge_id": knowledge_id}, context={"request": request}
        ).get_settings()
        return result.success({"mcp_config": config.get("mcp_config", {})})
