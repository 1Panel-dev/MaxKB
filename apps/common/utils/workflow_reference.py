from types import SimpleNamespace

from common.auth.authentication import get_is_permissions
from common.auth.constants.role_constants import RoleConstants
from common.auth.handle.impl.user_token import get_auth
from common.exception.app_exception import AppApiException
from django.utils.translation import gettext_lazy as _
from users.models import User


def authorized_resource_ids(resources, user_id, workspace_id, kind, permission):
    if not user_id or not workspace_id:
        return []
    user = User.objects.filter(id=user_id, is_active=True).first()
    if user is None:
        return []
    request = SimpleNamespace(user=user, auth=get_auth(user))
    permissions = (
        RoleConstants.ADMIN,
        RoleConstants.WORKSPACE_MANAGE.get_workspace_role(),
        permission.get_workspace_permission_workspace_manage_role(),
        getattr(permission, f"get_workspace_{kind}_permission")(),
    )
    ids = resources.filter(workspace_id=workspace_id).values_list("id", flat=True)
    return [
        str(pk)
        for pk in ids
        if get_is_permissions(request, workspace_id=workspace_id, **{f"{kind}_id": str(pk)})(*permissions)
    ]


def require_authorized_ids(requested, authorized):
    if set(map(str, requested)) - set(map(str, authorized)):
        raise AppApiException(403, _("No permission to access"))
