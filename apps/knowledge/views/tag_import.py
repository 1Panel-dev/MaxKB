from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import ViewPermission
from common.log.log import log
from common.result import result
from knowledge.api.tag_import import TagImportAPI, TagTemplateExportAPI
from knowledge.serializers.common import get_knowledge_operation_object
from knowledge.serializers.tag_import import TagImportSerializers


class KnowledgeTagImportView(APIView):
    authentication_classes = [TokenAuth]
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary=_("Import Knowledge Tags"),
        description=_("Upload an XLS or XLSX file with 标签 and 标签值 columns. Duplicate tags are skipped."),
        parameters=TagImportAPI.get_parameters(),
        request=TagImportAPI.get_request(),
        responses=TagImportAPI.get_response(),
        tags=[_("Knowledge Base/Tag")],
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_TAG_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_TAG_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            compare=CompareConstants.AND,
        ),
    )
    @log(
        menu="tag",
        operate="Import knowledge tags",
        get_operation_object=lambda r, keywords: get_knowledge_operation_object(keywords.get("knowledge_id")),
    )
    def post(self, request: Request, workspace_id: str, knowledge_id: str):
        return result.success(
            TagImportSerializers(data={"workspace_id": workspace_id, "knowledge_id": knowledge_id}).import_tags(
                request.data
            )
        )


class KnowledgeTagTemplateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        summary=_("Download Knowledge Tag Template"),
        parameters=TagTemplateExportAPI.get_parameters(),
        responses=TagTemplateExportAPI.get_response(),
        tags=[_("Knowledge Base/Tag")],
    )
    @has_permissions(
        PermissionConstants.KNOWLEDGE_TAG_CREATE.get_workspace_knowledge_permission(),
        PermissionConstants.KNOWLEDGE_TAG_CREATE.get_workspace_permission_workspace_manage_role(),
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        ViewPermission(
            [RoleConstants.USER.get_workspace_role()],
            [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
            compare=CompareConstants.AND,
        ),
    )
    def get(self, request: Request, workspace_id: str, knowledge_id: str):
        return TagImportSerializers(data={"workspace_id": workspace_id, "knowledge_id": knowledge_id}).export_template()
