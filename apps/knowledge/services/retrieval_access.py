"""Knowledge retrieval authorization using existing chat users and API keys."""

from dataclasses import dataclass

from django.db.models import QuerySet

from common.database_model_manage.database_model_manage import DatabaseModelManage
from knowledge.models import Knowledge
from system_manage.models import ChatUser, ChatUserApiKey


class RetrievalError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code, self.message, self.status = code, message, status


@dataclass(frozen=True)
class RetrievalIdentity:
    user_id: str | None = None
    api_key_id: str | None = None
    admin_user_id: str | None = None


def key_identity(key):
    if key is None or not key.is_active or not key.user.is_active:
        raise RetrievalError("invalid_api_key", "Invalid API key.", 401)
    return RetrievalIdentity(user_id=str(key.user_id), api_key_id=str(key.id))


def authenticate_key(authorization):
    if authorization is None:
        return RetrievalIdentity()
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer" or not 16 <= len(parts[1]) <= 1024:
        raise RetrievalError("invalid_api_key", "Invalid API key.", 401)
    return key_identity(QuerySet(ChatUserApiKey).select_related("user").filter(secret_key=parts[1]).first())


def refresh_identity(identity):
    if identity.api_key_id:
        return key_identity(QuerySet(ChatUserApiKey).select_related("user").filter(id=identity.api_key_id).first())
    return identity


def authorized_ids(user_id, ids):
    if not user_id or not QuerySet(ChatUser).filter(id=user_id, is_active=True).exists():
        return set()
    handler = DatabaseModelManage.get_model("get_knowledge_list_of_authorized")
    return set(map(str, handler(user_id, ids))) if handler else set()


def authorize_external(knowledge_id, identity):
    knowledge = QuerySet(Knowledge).filter(id=knowledge_id).first()
    if knowledge is None or knowledge.external_service.get("enabled") is not True:
        raise RetrievalError("service_unavailable", "Retrieval service is unavailable.", 404)
    if knowledge.external_service.get("authentication", False):
        if not identity.user_id:
            raise RetrievalError("authentication_required", "A chat user API key is required.", 401)
        if str(knowledge.id) not in authorized_ids(identity.user_id, [str(knowledge.id)]):
            raise RetrievalError("access_denied", "Knowledge access denied.", 403)
    return knowledge


def identity_from_server(user_id, user_type, debug=False):
    """Use authenticated server fields; form_data.asker is not an authorization identity."""
    return RetrievalIdentity(
        user_id=str(user_id) if user_id and user_type == "CHAT_USER" else None,
        admin_user_id=str(user_id) if user_id and debug and user_type in {"SYSTEM_USER", "ADMIN"} else None,
    )


def inherited_retrieval_context(parameters):
    return {
        key: parameters.get(key)
        for key in ("retrieval_identity", "chat_user_id", "chat_user_type", "workspace_id", "debug")
    }


def filter_admin_knowledge(knowledge, user_id):
    from common.auth.handle.impl.user_token import get_auth
    from common.exception.app_exception import AppUnauthorizedFailed
    from oss.serializers.file import _check_workspace_resource_permission
    from users.models import User

    user = QuerySet(User).filter(id=user_id, is_active=True).first()
    if user is None:
        return []
    auth = get_auth(user)
    allowed = []
    for item in knowledge:
        try:
            _check_workspace_resource_permission(
                auth,
                user.id,
                workspace_id=item.workspace_id,
                target_id=str(item.id),
                auth_target_type="KNOWLEDGE",
                read_permission="KNOWLEDGE:READ",
            )
            allowed.append(str(item.id))
        except AppUnauthorizedFailed:
            pass
    return allowed


def filter_workflow_knowledge(knowledge_ids, parameters):
    knowledge = list(QuerySet(Knowledge).filter(id__in=knowledge_ids))
    identity = parameters.get("retrieval_identity")
    if not isinstance(identity, RetrievalIdentity):
        identity = RetrievalIdentity()
    if identity.admin_user_id:
        return filter_admin_knowledge(knowledge, identity.admin_user_id)
    allowed, restricted, legacy = set(), [], []
    for item in knowledge:
        setting = item.external_service
        if "authentication" not in setting:
            legacy.append(str(item.id))
        elif setting["authentication"]:
            restricted.append(str(item.id))
        else:
            allowed.add(str(item.id))
    allowed.update(authorized_ids(identity.user_id, restricted) if restricted else [])
    # Preserve the pre-feature behavior for migrated, unconfigured knowledge bases.
    handler = DatabaseModelManage.get_model("get_knowledge_list_of_authorized")
    if legacy and handler and parameters.get("chat_user_type") == "CHAT_USER":
        legacy = handler(parameters.get("chat_user_id"), legacy)
    allowed.update(map(str, legacy))
    return [str(i) for i in knowledge_ids if str(i) in allowed]
