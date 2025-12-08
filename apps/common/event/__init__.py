# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py
    @date：2023/11/10 10:43
    @desc:
"""
from django.core.cache import cache
from django.db.models import QuerySet
from django.utils.translation import gettext as _


from ..constants.cache_version import Cache_Version
from ..db.sql_execute import update_execute
from ..utils.lock import RedisLock

update_document_status_sql = """
                             UPDATE "public"."document"
                             SET status ="replace"("replace"("replace"(status, '1', '3'), '0', '3'), '4', '3')
                             WHERE status ~ '1|0|4' \
                             """


def run():
    from models_provider.models import Model, Status
    rlock = RedisLock()
    if rlock.try_lock('event_init', 30 * 30):
        try:
            # 修改Model状态为ERROR
            QuerySet(Model).filter(
                status=Status.DOWNLOAD
            ).update(
                status=Status.ERROR, meta={'message': _('The download process was interrupted, please try again')}
            )
            # 更新文档状态
            update_execute(update_document_status_sql, [])
            version, get_key = Cache_Version.SYSTEM.value
            cache.delete(get_key(key='rsa_key'), version=version)
        finally:
            rlock.un_lock('event_init')
