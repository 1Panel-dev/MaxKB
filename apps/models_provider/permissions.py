from common.auth.authentication import get_is_permissions
from common.constants.permission_constants import CompareConstants, PermissionConstants, RoleConstants, ViewPermission
from common.database_model_manage.database_model_manage import DatabaseModelManage
from models_provider.models import Model

WORKSPACE_MODEL_READ_PERMISSIONS = (
    PermissionConstants.MODEL_READ.get_workspace_model_permission(),
    PermissionConstants.MODEL_READ.get_workspace_permission_workspace_manage_role(),
    RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
    ViewPermission([RoleConstants.USER.get_workspace_role()],
                   [PermissionConstants.MODEL.get_workspace_model_permission()], CompareConstants.AND),
)


def can_read_model(request, workspace_id, model):
    if model.workspace_id == "None":
        get_authorized_model = DatabaseModelManage.get_model("get_authorized_model")
        return get_authorized_model is not None and get_authorized_model(
            Model.objects.filter(id=model.id, workspace_id="None"), workspace_id
        ).exists()
    return model.workspace_id == workspace_id and get_is_permissions(
        request, workspace_id=workspace_id, model_id=model.id
    )(*WORKSPACE_MODEL_READ_PERMISSIONS)
