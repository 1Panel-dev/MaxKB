# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： chat_history.py
@date：2025/6/9 11:23
@desc: 会话历史的滚动窗口缓存（Redis，跨 worker 共享）。

- 历史是 append-only：每轮末尾追加一条已完成记录，旧记录不再变。
- 只缓存最近 LIMIT 条，且只存历史真正要用的字段：question + messages
  （新流程用 question/messages 构造 Human/AI message，不再用 problem_text/answer_text）。
- 缓存缺失时回落 DB 并回填；记录定稿(on_complete)后 append/按 id upsert；清历史时失效。
"""

from django.core.cache import cache
from django.db.models import QuerySet

from application.models import ChatRecord
from common.constants.cache_version import Cache_Version


class ChatHistory:
    # 最近多少条历史进上下文（注意：若节点 dialogue_number 超过该值会喂不够）
    LIMIT = 5
    TIMEOUT = 60 * 30

    def __init__(self, chat_id):
        self.chat_id = str(chat_id)

    def _key(self):
        return Cache_Version.CHAT_HISTORY.get_key(key=self.chat_id)

    def _version(self):
        return Cache_Version.CHAT_HISTORY.get_version()

    @staticmethod
    def _to_map(r):
        return {
            "id": str(r.id),
            "chat_id": str(r.chat_id),
            "question": r.question,
            "messages": r.messages,
            "create_time": r.create_time,
        }

    @staticmethod
    def _from_map(d):
        return ChatRecord(
            id=d.get("id"),
            chat_id=d.get("chat_id"),
            question=d.get("question"),
            messages=d.get("messages"),
            create_time=d.get("create_time"),
        )

    def _load_from_db(self):
        records = list(QuerySet(ChatRecord).filter(chat_id=self.chat_id).order_by("-create_time")[0 : self.LIMIT])
        records.sort(key=lambda r: r.create_time)
        return records

    def load(self, exclude_record_id=None):
        """
        读历史：命中缓存则还原，未命中从 DB 取最近 N 条并回填。
        exclude_record_id：重答/Form 提交时把当前这条从历史上下文里剔掉。
        """
        cached = cache.get(self._key(), version=self._version())
        if cached is None:
            records = self._load_from_db()
            cache.set(self._key(), [self._to_map(r) for r in records], version=self._version(), timeout=self.TIMEOUT)
        else:
            records = [self._from_map(d) for d in cached]
        if exclude_record_id is not None:
            records = [r for r in records if str(r.id) != str(exclude_record_id)]
        return records

    def append(self, chat_record):
        """
        记录定稿后追加进缓存（按 create_time 天然排在最后）。
        re_chat 复用同一 id → 先按 id 去重再追加，等价 upsert。
        未预热(缓存为空)则跳过，下次 load 会从 DB 重建。
        """
        cached = cache.get(self._key(), version=self._version())
        if cached is None:
            return
        cached = [d for d in cached if str(d.get("id")) != str(chat_record.id)]
        cached.append(self._to_map(chat_record))
        cache.set(self._key(), cached[-self.LIMIT :], version=self._version(), timeout=self.TIMEOUT)

    def clear(self):
        cache.delete(self._key(), version=self._version())
