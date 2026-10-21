# coding=utf-8
"""
@project: MaxKB
@file： message_bus.py
@desc: 基于 Redis Pub/Sub 的跨进程、跨系统消息总线。提供 emit / on 两个接口。
"""

import json
import threading
from typing import Callable, Dict, List

from common.utils.logger import maxkb_logger

CHANNEL = "maxkb:bus"

_handlers: Dict[str, List[Callable]] = {}
_handlers_lock = threading.Lock()

_subscriber_started = False
_subscriber_thread = None
_subscriber_lock = threading.Lock()


def _redis_client():
    """取底层 redis-py 客户端（含 pubsub 能力），已由 Django settings 配置支持 sentinel/普通 Redis。"""
    from django_redis import get_redis_connection

    return get_redis_connection("default")


def _start_subscriber() -> None:
    """懒启动：每个进程只起一条 daemon 订阅线程；线程因建连失败退出后，下次调用会重新拉起。"""
    global _subscriber_started, _subscriber_thread
    if _subscriber_started and _subscriber_thread is not None and _subscriber_thread.is_alive():
        return
    with _subscriber_lock:
        if _subscriber_started and _subscriber_thread is not None and _subscriber_thread.is_alive():
            return
        _subscriber_started = True
        _subscriber_thread = threading.Thread(target=_listen, name="maxkb-bus", daemon=True)
        _subscriber_thread.start()


def _listen() -> None:
    # 建连失败(Redis 不可用)则记日志退出,不自动重连;由 emit 检测线程存活后重新拉起。
    # 建连成功后的消息循环由 redis-py 内部维持,无需自行重连。
    ps = None
    try:
        ps = _redis_client().pubsub(ignore_subscribe_messages=True)
        ps.subscribe(CHANNEL)
        for message in ps.listen():
            _dispatch(message)
    except Exception as e:
        maxkb_logger.error(f"Message bus subscriber failed: {e}")
    finally:
        if ps is not None:
            try:
                ps.close()
            except Exception:
                pass


def _dispatch(message) -> None:
    try:
        data = message.get("data")
        if isinstance(data, (bytes, bytearray)):
            data = data.decode("utf-8")
        body = json.loads(data)
        event = body.get("event")
        if not event:
            return
        args = body.get("args")
        for handler in list(_handlers.get(event, ())):
            try:
                handler(args)
            except Exception as e:
                maxkb_logger.error(f"Message bus handler error for event[{event}]: {e}")
    except Exception as e:
        maxkb_logger.error("Failed to dispatch message bus event: %s", e)


def on(event: str, handler: Callable) -> None:
    """
    注册一个事件监听，本进程内生效；收到该事件时异步调用 handler(args)。
    :param event: 事件名称
    :param handler: 回调函数 def handler(args):
                                pass
    """
    with _handlers_lock:
        _handlers.setdefault(event, []).append(handler)
    _start_subscriber()


def emit(event: str, args=None) -> bool:
    """
    向所有进程广播一个事件。Redis 不可用时返回 False。
    :param event: 事件名称
    :param args: 事件参数
    """
    _start_subscriber()
    try:
        _redis_client().publish(
            CHANNEL,
            json.dumps({"event": event, "args": args}, ensure_ascii=False),
        )
        return True
    except Exception as e:
        maxkb_logger.warning(f"Message bus emit[{event}] failed: {e}")
        return False
