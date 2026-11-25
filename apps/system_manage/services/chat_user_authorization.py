from types import SimpleNamespace

from django.utils.translation import gettext_lazy as _

from application.models import ApplicationAccessToken, ChatUserType
from common.auth.constants.chat_permission_constants import ChatPermissionConstants
from common.auth.handle.impl.chat_user_token import get_auth
from common.exception.app_exception import AppApiException
from system_manage.models import ChatUser


def ensure_application_chat_user_authorized(
    application_id,
    chat_user_id,
    *,
    chat_user_type=ChatUserType.CHAT_USER.value,
    debug=False,
):
    if debug or chat_user_type != ChatUserType.CHAT_USER.value:
        return
    if not ApplicationAccessToken.objects.filter(application_id=application_id, authentication=True).exists():
        return

    chat_user = ChatUser.objects.filter(id=chat_user_id).only("source").first()
    if chat_user is None:
        raise AppApiException(1005, _("The user does not have permission to access the application"))

    login_type = str(chat_user.source or "").upper()
    auth = get_auth(login_type, chat_user_id, application_id)
    if not ChatPermissionConstants.get_aggregate_permissions().hasPermission(
        SimpleNamespace(auth=auth),
        application_id=application_id,
    ):
        raise AppApiException(1005, _("The user does not have permission to access the application"))


def ensure_workflow_application_chat_user_authorized(application_id, workflow_params):
    ensure_application_chat_user_authorized(
        application_id,
        workflow_params.get("chat_user_id"),
        chat_user_type=workflow_params.get("chat_user_type"),
        debug=workflow_params.get("debug", False),
    )
