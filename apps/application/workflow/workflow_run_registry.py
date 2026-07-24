# coding=utf-8
"""
    @project: MaxKB
    @file： workflow_run_registry.py
    @desc: 工作流运行注册表，用于管理和取消正在运行的工作流实例
"""
import threading
from enum import Enum

from common.utils.logger import maxkb_logger


class CancelResult(Enum):
    """取消操作结果"""
    CANCELLED = "CANCELLED"
    NOT_FOUND = "NOT_FOUND"
    FAILED = "FAILED"


class WorkflowRunRegistry:
    _lock = threading.Lock()
    _running = {}  # {chat_record_id: WorkflowManage}
    _chat_to_records = {}  # {chat_id: set[chat_record_id]}

    @classmethod
    def register(cls, chat_record_id: str, chat_id: str, workflow_manage) -> None:
        """
        注册一个正在运行的工作流实例
        @param chat_record_id: 聊天记录ID
        @param chat_id: 聊天ID
        @param workflow_manage: WorkflowManage 实例
        """
        if not chat_record_id or not workflow_manage:
            return
        with cls._lock:
            cls._running[str(chat_record_id)] = workflow_manage
            if chat_id:
                if chat_id not in cls._chat_to_records:
                    cls._chat_to_records[chat_id] = set()
                cls._chat_to_records[chat_id].add(str(chat_record_id))
            maxkb_logger.debug(f"Workflow registered: {chat_record_id}, total running: {len(cls._running)}")

    @classmethod
    def unregister(cls, chat_record_id: str, chat_id: str = None) -> None:
        """
        注销一个工作流实例（无论成功/失败/取消都应调用）
        @param chat_record_id: 聊天记录ID
        @param chat_id: 聊天ID
        """
        if not chat_record_id:
            return
        with cls._lock:
            removed = cls._running.pop(str(chat_record_id), None)
            if chat_id and chat_id in cls._chat_to_records:
                cls._chat_to_records[chat_id].discard(str(chat_record_id))
                if not cls._chat_to_records[chat_id]:
                    del cls._chat_to_records[chat_id]
            if removed is not None:
                maxkb_logger.debug(f"Workflow unregistered: {chat_record_id}, total running: {len(cls._running)}")

    @classmethod
    def cancel_by_chat_id(cls, chat_id: str) -> CancelResult:
        """
        取消某个聊天下所有运行中的工作流
        @param chat_id: 聊天ID
        @return: CancelResult
        """
        if not chat_id:
            return CancelResult.NOT_FOUND

        with cls._lock:
            record_ids = list(cls._chat_to_records.get(chat_id, set()))

        if not record_ids:
            maxkb_logger.info(f"Cancel requested but no running workflow found for chat: {chat_id}")
            return CancelResult.NOT_FOUND

        cancelled_count = 0
        failed_count = 0
        for record_id in record_ids:
            with cls._lock:
                wm = cls._running.get(record_id)
            if wm:
                try:
                    wm.cancel()
                    cancelled_count += 1
                    maxkb_logger.info(f"Cancel signal sent to workflow: {record_id}")
                except Exception as e:
                    failed_count += 1
                    maxkb_logger.error(f"Failed to cancel workflow: {record_id}, error: {e}")

        if failed_count > 0 and cancelled_count == 0:
            return CancelResult.FAILED
        return CancelResult.CANCELLED

    @classmethod
    def cancel_by_record_id(cls, chat_record_id: str) -> CancelResult:
        """
        取消某个特定的工作流
        @param chat_record_id: 聊天记录ID
        @return: CancelResult
        """
        if not chat_record_id:
            return CancelResult.NOT_FOUND

        with cls._lock:
            wm = cls._running.get(str(chat_record_id))

        if wm is None:
            maxkb_logger.info(f"Cancel requested but workflow not found (may already finished): {chat_record_id}")
            return CancelResult.NOT_FOUND

        try:
            wm.cancel()
            maxkb_logger.info(f"Cancel signal sent to workflow: {chat_record_id}")
            return CancelResult.CANCELLED
        except Exception as e:
            maxkb_logger.error(f"Failed to cancel workflow: {chat_record_id}, error: {e}")
            return CancelResult.FAILED

    @classmethod
    def get(cls, chat_record_id: str):
        """
        获取正在运行的工作流实例
        @param chat_record_id: 聊天记录ID
        @return: WorkflowManage 实例或 None
        """
        if not chat_record_id:
            return None
        return cls._running.get(str(chat_record_id))

    @classmethod
    def is_running(cls, chat_record_id: str) -> bool:
        """
        检查工作流是否正在运行
        @param chat_record_id: 聊天记录ID
        @return: 是否正在运行
        """
        return chat_record_id is not None and str(chat_record_id) in cls._running

    @classmethod
    def is_chat_running(cls, chat_id: str) -> bool:
        """
        检查某个聊天是否有正在运行的工作流
        @param chat_id: 聊天ID
        @return: 是否有正在运行的工作流
        """
        if not chat_id:
            return False
        with cls._lock:
            return chat_id in cls._chat_to_records and len(cls._chat_to_records[chat_id]) > 0

    @classmethod
    def running_count(cls) -> int:
        """
        获取正在运行的工作流数量
        @return: 数量
        """
        return len(cls._running)

    @classmethod
    def running_ids(cls) -> list:
        """
        获取所有正在运行的工作流ID列表
        @return: ID列表
        """
        with cls._lock:
            return list(cls._running.keys())
