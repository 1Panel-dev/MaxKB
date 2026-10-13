from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore

from common.utils.logger import maxkb_logger


class SafeDjangoJobStore(DjangoJobStore):
    """
    DjangoJobStore 在目标 job 已被删除时会抛出 JobLookupError。

    多个 celery worker(进程/线程)共享同一张 django_apscheduler_djangojob 表,
    任一进程删除 job 后, 其它进程在调度该 job 的过程中就会命中这两个异常:
    update_job 找不到记录, remove_job 找不到记录。
    该异常会从 APScheduler 的调度主循环(apscheduler.schedulers.base._process_jobs)
    直接冒泡出去并终止 'APScheduler' 线程, 导致该进程内所有定时任务永久停摆,
    因此这里把 "job 已不存在" 视为正常情况处理。
    """

    def update_job(self, job):
        try:
            super().update_job(job)
        except JobLookupError:
            maxkb_logger.warning(f"Skip update of job [{job.id}], it has been removed already")

    def remove_job(self, job_id):
        try:
            super().remove_job(job_id)
        except JobLookupError:
            pass


scheduler = BackgroundScheduler()
scheduler.add_jobstore(SafeDjangoJobStore(), "default")

try:
    scheduler.start()
except Exception as e:
    maxkb_logger.error(f"Failed to start scheduler: {e}")
