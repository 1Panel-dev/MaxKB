"""Worker entry points for managing knowledge synchronization schedules."""

from ops import celery_app


@celery_app.task(name="celery:deploy_knowledge_sync_job")
def deploy_knowledge_sync_job(knowledge_id: str):
    # Importing the scheduler starts it; keep that import in the worker process.
    from knowledge.services.knowledge_sync_schedule import deploy_knowledge_sync_job as deploy

    return deploy(knowledge_id)


@celery_app.task(name="celery:remove_knowledge_sync_job")
def remove_knowledge_sync_job(knowledge_id: str):
    from knowledge.services.knowledge_sync_schedule import remove_knowledge_sync_job as remove

    return remove(knowledge_id)
