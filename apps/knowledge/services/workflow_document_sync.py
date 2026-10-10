"""Run one workflow Web document through its original data-source branch."""

from copy import deepcopy

from common.exception.app_exception import AppApiException
from django.db import transaction
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from knowledge.models import (
    DocumentResourceType,
    Knowledge,
    KnowledgeSyncLog,
    KnowledgeSyncStatus,
    KnowledgeType,
    KnowledgeWorkflow,
)
from knowledge.services.sync_status import recover_stale_sync_logs
from knowledge.services.workflow_sync import has_running_workflow_document_sync
from knowledge.services.workflow_sync_source import DOCUMENT_IDENTITY_FIELDS


def is_workflow_web_document(document) -> bool:
    meta = document.meta or {}
    return (
        document.type == KnowledgeType.WORKFLOW
        and document.resource_type == DocumentResourceType.DOCUMENT
        and meta.get("source_type") == "web"
    )


def workflow_document_sync_input(knowledge, workflow, document) -> tuple[dict, dict]:
    meta = document.meta or {}
    node_id = meta.get("source_node_id")
    source_node = next(
        (node for node in (workflow.work_flow or {}).get("nodes", []) if node.get("id") == node_id), None
    )
    if not is_workflow_web_document(document) or not meta.get("source_url") or not meta.get("source_scope"):
        raise AppApiException(400, _("Workflow Web document is missing its source information"))
    if source_node is None or source_node.get("type") != "data-source-web-node":
        raise AppApiException(400, _("The original Web data source no longer exists in the knowledge workflow"))
    saved_input = deepcopy((knowledge.meta or {}).get("workflow_sync_input") or {})
    # Retain knowledge-base inputs; a single-document run must never upload saved local files.
    workflow_input = {
        "data_source": {
            "node_id": node_id,
            "source_url": meta["source_url"],
            "selector": meta.get("selector") or "body",
        },
        "knowledge_base": saved_input.get("knowledge_base") or {},
    }
    source_meta = {
        field: meta[field]
        for field in (*DOCUMENT_IDENTITY_FIELDS, "source_scope", "source_node_id", "source_type")
        if meta.get(field)
    }
    return workflow_input, {"id": str(document.id), "name": document.name, "source_meta": source_meta}


@transaction.atomic
def sync_workflow_web_document(document, user=None):
    # Import lazily: the workflow serializer also uses DocumentSerializers.
    from knowledge.serializers.knowledge_workflow import KnowledgeWorkflowActionSerializer

    knowledge = QuerySet(Knowledge).select_for_update().get(id=document.knowledge_id)
    workflow = QuerySet(KnowledgeWorkflow).filter(knowledge_id=knowledge.id).first()
    if knowledge.type != KnowledgeType.WORKFLOW or workflow is None:
        raise AppApiException(400, _("Knowledge workflow does not exist"))
    workflow_input, sync_document = workflow_document_sync_input(knowledge, workflow, document)
    user = user or knowledge.user
    if user is None:
        raise AppApiException(400, _("Workflow knowledge has no owner available for synchronization"))
    recover_stale_sync_logs(knowledge.id)
    if QuerySet(KnowledgeSyncLog).filter(
        knowledge_id=knowledge.id, status=KnowledgeSyncStatus.RUNNING
    ).exists() or has_running_workflow_document_sync(knowledge.id):
        raise AppApiException(409, _("Synchronization is already running"))
    # Reserve an execution under the knowledge lock; launch its nodes after commit.
    KnowledgeWorkflowActionSerializer(
        data={"knowledge_id": str(knowledge.id), "workspace_id": knowledge.workspace_id}
    ).action(workflow_input, user, True, sync_document=sync_document)
    return True
