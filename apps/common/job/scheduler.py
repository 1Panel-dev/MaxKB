from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

try:
    scheduler.start()
except Exception as e:
    from common.utils.logger import maxkb_logger

    maxkb_logger.error(f"Failed to start scheduler: {e}")
