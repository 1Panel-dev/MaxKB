"""Worker entry points for knowledge synchronization schedules and image previews."""

from celery.signals import worker_init
from common.utils.logger import maxkb_logger
from ops import celery_app


@celery_app.task(name="celery:process_image_preview")
def process_image_preview(workspace_id: str, knowledge_id: str, preview_id: str, user_id=None):
    from knowledge.services.image_documents import ImageDocumentService

    ImageDocumentService(workspace_id, knowledge_id, user_id).process_preview(preview_id)


@celery_app.task(name="celery:process_paragraph_visual_assets")
def process_paragraph_visual_assets(paragraph_ids: list[str]):
    from knowledge.services.paragraph_assets import process_pending_visual_assets

    process_pending_visual_assets(paragraph_ids)


@worker_init.connect
def fail_interrupted_knowledge_synchronizations(sender=None, **kwargs):
    from knowledge.services.sync_status import fail_running_sync_logs_on_startup

    failed = fail_running_sync_logs_on_startup()
    if failed:
        maxkb_logger.info(f"Marked {failed} interrupted knowledge synchronizations as failed on startup")


@celery_app.task(name="celery:deploy_knowledge_sync_job")
def deploy_knowledge_sync_job(knowledge_id: str):
    # Importing the scheduler starts it; keep that import in the worker process.
    from knowledge.services.knowledge_sync_schedule import deploy_knowledge_sync_job as deploy

    return deploy(knowledge_id)


@celery_app.task(name="celery:remove_knowledge_sync_job")
def remove_knowledge_sync_job(knowledge_id: str):
    from knowledge.services.knowledge_sync_schedule import remove_knowledge_sync_job as remove

    return remove(knowledge_id)
