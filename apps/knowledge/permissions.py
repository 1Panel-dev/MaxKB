from common.auth.authentication import check_batch_permissions, get_is_permissions
from common.constants.permission_constants import CompareConstants, PermissionConstants, RoleConstants, ViewPermission
from common.database_model_manage.database_model_manage import DatabaseModelManage
from knowledge.models import Knowledge, KnowledgeScope

TAG_READ_PERMISSIONS = (
    PermissionConstants.KNOWLEDGE_TAG_READ.get_workspace_knowledge_permission(),
    PermissionConstants.KNOWLEDGE_TAG_READ.get_workspace_permission_workspace_manage_role(),
    RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    ViewPermission([RoleConstants.USER.get_workspace_role()],
                   [PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()], CompareConstants.AND),
)

SHARED_WORKSPACE_TAG_READ_PERMISSIONS = (
    PermissionConstants.KNOWLEDGE_TAG_READ.get_workspace_permission(),
    RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    RoleConstants.USER.get_workspace_role(),
)


def workspace_tag_knowledge(request, workspace_id, knowledge_ids):
    permitted_ids = check_batch_permissions(
        request, knowledge_ids, 'knowledge_id', TAG_READ_PERMISSIONS, workspace_id=workspace_id
    )
    local = Knowledge.objects.filter(scope=KnowledgeScope.WORKSPACE, workspace_id=workspace_id, id__in=permitted_ids)
    authorize_shared = DatabaseModelManage.get_model('get_authorized_knowledge')
    if authorize_shared and get_is_permissions(request, workspace_id=workspace_id)(
        *SHARED_WORKSPACE_TAG_READ_PERMISSIONS
    ):
        shared = Knowledge.objects.filter(scope=KnowledgeScope.SHARED, id__in=knowledge_ids)
        return local | authorize_shared(shared, workspace_id)
    return local
