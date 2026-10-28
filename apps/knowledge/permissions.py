"""Workspace knowledge permissions and resource-type-aware document authorization."""

from functools import partial

from common.auth.constants.compare_constants import CompareConstants
from common.auth.constants.permission_constants import PermissionConstants
from common.auth.constants.role_constants import RoleConstants
from common.auth.struct.aggregate_permission import AggregatePermission
from common.exception.app_exception import AppUnauthorizedFailed
from django.utils.translation import gettext_lazy as _
from knowledge.models import Document, DocumentResourceType, Knowledge, TaskType
from rest_framework import serializers


def knowledge_permission(permission):
    """Preserve workspace administrators, explicit ownership and scoped grants."""
    return AggregatePermission(
        roles=[RoleConstants.ADMIN, RoleConstants.WORKSPACE_MANAGE.get_workspace_role()],
        permissions=[
            permission.get_workspace_knowledge_permission(),
            permission.get_workspace_permission_workspace_manage_role(),
        ],
        aggregatePermissions=[
            AggregatePermission(
                roles=[RoleConstants.USER.get_workspace_role()],
                permissions=[PermissionConstants.KNOWLEDGE.get_workspace_knowledge_permission()],
                compare=CompareConstants.AND,
            )
        ],
    )


def has_knowledge_permission(request, workspace_id, knowledge_id, *permissions):
    return any(
        knowledge_permission(permission).hasPermission(request, workspace_id=workspace_id, knowledge_id=knowledge_id)
        for permission in permissions
    )


def document_list_permission(request, kwargs):
    permission = (
        PermissionConstants.KNOWLEDGE_IMAGE_READ
        if request.query_params.get("resource_type") == DocumentResourceType.IMAGE
        else PermissionConstants.KNOWLEDGE_DOCUMENT_READ
    )
    return knowledge_permission(permission)


def document_permission(document, image):
    """Choose the permission using persisted type, never a client-supplied type."""

    def resolve(request, kwargs):
        is_image = Document.objects.filter(
            knowledge_id=kwargs["knowledge_id"],
            knowledge__workspace_id=kwargs["workspace_id"],
            id=kwargs["document_id"],
            resource_type=DocumentResourceType.IMAGE,
        ).exists()
        if is_image and image is None:
            raise AppUnauthorizedFailed(403, _("No permission to access"))
        return knowledge_permission(image if is_image else document)

    return resolve


def batch_document_permission(document, image, *, id_field="id_list"):
    """Every selected resource type must have its corresponding permission."""

    def resolve(request, kwargs):
        ids = request.data if id_field is None else request.data.get(id_field, [])
        ids = serializers.ListField(child=serializers.UUIDField(), allow_empty=False).run_validation(ids)
        resource_types = list(
            Document.objects.filter(
                knowledge_id=kwargs["knowledge_id"], knowledge__workspace_id=kwargs["workspace_id"], id__in=ids
            )
            .values_list("resource_type", flat=True)
            .distinct()
        )
        if image is None and DocumentResourceType.IMAGE in resource_types:
            raise AppUnauthorizedFailed(403, _("No permission to access"))
        return AggregatePermission(
            aggregatePermissions=[
                knowledge_permission(image if resource_type == DocumentResourceType.IMAGE else document)
                for resource_type in resource_types
            ]
            or [knowledge_permission(document)],
            compare=CompareConstants.AND,
        )

    return resolve


_TASK_PERMISSIONS = {
    TaskType.EMBEDDING.value: (
        PermissionConstants.KNOWLEDGE_DOCUMENT_VECTOR,
        PermissionConstants.KNOWLEDGE_IMAGE_VECTOR,
    ),
    TaskType.GENERATE_PROBLEM.value: (
        PermissionConstants.KNOWLEDGE_DOCUMENT_GENERATE,
        PermissionConstants.KNOWLEDGE_IMAGE_GENERATE,
    ),
    TaskType.TOKENIZE.value: (PermissionConstants.KNOWLEDGE_DOCUMENT_TOKEN, PermissionConstants.KNOWLEDGE_IMAGE_TOKEN),
}


def cancel_document_task_permission(*, batch=False):
    factory = batch_document_permission if batch else document_permission

    def resolve(request, kwargs):
        permissions = _TASK_PERMISSIONS.get(
            request.data.get("type"),
            (PermissionConstants.KNOWLEDGE_DOCUMENT_EDIT, PermissionConstants.KNOWLEDGE_IMAGE_EDIT),
        )
        return factory(*permissions)(request, kwargs)

    return resolve


def check_knowledge_edit_permission(request, workspace_id, knowledge_id):
    """Mixed settings updates must satisfy every submitted field's permission."""
    if not isinstance(request.data, dict):
        raise serializers.ValidationError(_("Expected an object"))
    allowed = partial(has_knowledge_permission, request, workspace_id, knowledge_id)
    if "doc_strategy" in request.data and not allowed(PermissionConstants.KNOWLEDGE_DOCUMENT_STRATEGY_EDIT):
        raise AppUnauthorizedFailed(403, _("No permission to access"))
    meta = request.data.get("meta")
    if isinstance(meta, dict):
        stored_meta = (
            Knowledge.objects.filter(id=knowledge_id, workspace_id=workspace_id).values_list("meta", flat=True).first()
            or {}
        )
        for key, permission in [
            ("doc_strategy", PermissionConstants.KNOWLEDGE_DOCUMENT_STRATEGY_EDIT),
            ("sync_setting", PermissionConstants.KNOWLEDGE_SCHEDULED_SYNC_EDIT),
        ]:
            if key in meta and meta[key] != stored_meta.get(key) and not allowed(permission):
                raise AppUnauthorizedFailed(403, _("No permission to access"))
    other_fields = set(request.data) - {"doc_strategy"}
    if other_fields - {"name", "desc"}:
        if not allowed(PermissionConstants.KNOWLEDGE_SETTING_EDIT):
            raise AppUnauthorizedFailed(403, _("No permission to access"))
    elif other_fields or not request.data:
        if not allowed(
            PermissionConstants.KNOWLEDGE_EDIT,
            PermissionConstants.KNOWLEDGE_SETTING_EDIT,
        ):
            raise AppUnauthorizedFailed(403, _("No permission to access"))


def check_knowledge_detail_permission(request, workspace_id, knowledge_id):
    """Explicit settings sections require their own read permissions."""
    allowed = partial(has_knowledge_permission, request, workspace_id, knowledge_id)
    section = request.query_params.get("section")
    if section == "setting" and not allowed(PermissionConstants.KNOWLEDGE_SETTING_READ):
        raise AppUnauthorizedFailed(403, _("No permission to access"))
    if section == "document_strategy" and not allowed(PermissionConstants.KNOWLEDGE_DOCUMENT_STRATEGY_READ):
        raise AppUnauthorizedFailed(403, _("No permission to access"))


def filter_knowledge_detail(request, workspace_id, knowledge_id, detail):
    """Remove separately authorized configuration from GET and PUT responses."""
    allowed = partial(has_knowledge_permission, request, workspace_id, knowledge_id)
    if not allowed(
        PermissionConstants.KNOWLEDGE_SETTING_READ,
        PermissionConstants.KNOWLEDGE_SETTING_EDIT,
    ):
        detail["meta"] = {}
    else:
        detail["meta"] = dict(detail.get("meta") or {})
    if not allowed(
        PermissionConstants.KNOWLEDGE_DOCUMENT_STRATEGY_READ,
        PermissionConstants.KNOWLEDGE_DOCUMENT_STRATEGY_EDIT,
    ):
        detail["doc_strategy"] = None
        detail["meta"].pop("doc_strategy", None)
    if not allowed(
        PermissionConstants.KNOWLEDGE_SCHEDULED_SYNC_READ,
        PermissionConstants.KNOWLEDGE_SCHEDULED_SYNC_EDIT,
    ):
        detail["meta"].pop("sync_setting", None)
    return detail
