# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py
    @date：2023/11/10 10:43
    @desc:
"""
import setting.models
from setting.models import Model
from .listener_manage import *
from django.utils.translation import gettext as _

from ..db.sql_execute import update_execute
from common.lock.impl.file_lock import FileLock

lock = FileLock()
update_document_status_sql = """
UPDATE "public"."document" 
SET status ="replace"("replace"("replace"(status, '1', '3'), '0', '3'), '4', '3')
WHERE status ~ '1|0|4'
"""


def run():
    if lock.try_lock('event_init', 30 * 30):
        try:
            QuerySet(Model).filter(status=setting.models.Status.DOWNLOAD).update(status=setting.models.Status.ERROR,
                                                                                 meta={'message': _(
                                                                                     'The download process was interrupted, please try again')})
            update_execute(update_document_status_sql, [])
        finally:
            lock.un_lock('event_init')
