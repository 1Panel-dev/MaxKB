# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： message_queue.py
    @date：2026/7/27  10:10
    @desc: 消息队列管理，用于流式响应的消息存储和消费
    支持多消费者、断线重连、消息持久化
"""
import bisect
import fnmatch
import json
import socket
import threading
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, List, Optional, Tuple

from common.utils.logger import maxkb_logger

DEFAULT_TTL = 3600
DEFAULT_BATCH_SIZE = 100
DEFAULT_BLOCK_TIMEOUT_MS = 5000
MAX_CONSECUTIVE_ERRORS = 5
# XREAD block 窗口相对 socket_timeout 的安全比例，保证服务端先返回、客户端后超时
BLOCK_SAFETY_RATIO = 0.6


def _benign_timeouts() -> tuple:
    """
    阻塞读读空窗口时的超时属于正常现象，不能计入故障预算。
    redis.exceptions.TimeoutError 与内建 TimeoutError/socket.timeout 都要覆盖。
    """
    candidates = [TimeoutError, socket.timeout]
    try:
        from redis.exceptions import TimeoutError as RedisTimeoutError
        candidates.append(RedisTimeoutError)
    except ImportError:
        pass
    return tuple({c for c in candidates if isinstance(c, type)})


BENIGN_TIMEOUTS = _benign_timeouts()


class MessageQueueError(Exception):
    """
    队列后端不可用。

    刻意与"队列不存在"区分开：Redis 抖动不应该被上层误判成会话已失效。
    """


class MessageStatus(str, Enum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    CANCELLED = "CANCELLED"


def parse_stream_id(value: Any) -> Tuple[int, int]:
    """
    把 Redis Stream ID ("1699999999999-0") 解析成可比较的元组。
    非法值一律退化成 (0, 0)，即"从头开始"。
    """
    if value is None:
        return 0, 0
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8")
    value = str(value)
    if not value or value == "0":
        return 0, 0
    if value == "$":
        return (1 << 63) - 1, 0
    parts = value.split("-", 1)
    try:
        ms = int(parts[0])
        seq = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        return ms, seq
    except (TypeError, ValueError):
        return 0, 0


class IMessageQueue(ABC):
    """消息队列接口"""

    @abstractmethod
    def exists(self, queue_id: str) -> bool:
        pass

    @abstractmethod
    def produce(self, queue_id: str, message: Any, ttl: int = None) -> None:
        pass

    @abstractmethod
    def produce_done(self, queue_id: str, ttl: int = None) -> None:
        pass

    @abstractmethod
    def is_done(self, queue_id: str) -> bool:
        pass

    @abstractmethod
    def consume(
            self,
            queue_id: str,
            start_id: str = "0",
            on_message: Optional[Callable[[str, str], None]] = None,
            on_done: Optional[Callable[[], None]] = None,
            timeout: float = 300,
            should_stop: Optional[Callable[[], bool]] = None,
    ) -> None:
        """
        消费消息，阻塞直到队列结束 / 超时 / 被取消。

        @param start_id:    起始消息ID，"0" 表示从头；语义为"返回 ID 严格大于 start_id 的消息"
        @param on_message:  回调 (message_id, message_data)
        @param on_done:     结束回调，保证有且只调用一次
        @param timeout:     最长消费时间（秒）
        @param should_stop: 取消钩子，返回 True 则立即结束消费
        """
        pass

    @abstractmethod
    def get_messages(self, queue_id: str, start_id: str = "0", count: int = 100) -> list:
        """拉取 ID 严格大于 start_id 的历史消息，用于断线重连补发。"""
        pass

    @abstractmethod
    def delete(self, queue_id: str) -> None:
        pass

    @abstractmethod
    def clear_by_pattern(self, pattern: str) -> int:
        pass


_instances: dict[str, IMessageQueue] = {}
_instances_lock = threading.Lock()


class InMemoryMessageQueue(IMessageQueue):
    """内存消息队列，仅适用于单进程环境（多 worker 下生产者和消费者可能不在同一进程）"""

    def __init__(self, default_ttl: int = DEFAULT_TTL):
        # queue_id -> (sort_keys, items)，两个列表下标一一对应，便于 bisect 定位游标
        self._sort_keys: dict[str, List[Tuple[int, int]]] = {}
        self._items: dict[str, List[Tuple[str, str]]] = {}
        self._done_flags: dict[str, bool] = {}
        self._last_id: dict[str, Tuple[int, int]] = {}
        self._expire_at: dict[str, float] = {}
        self._default_ttl = default_ttl
        # 用 RLock，避免 clear_by_pattern -> delete 这类内部复用造成自死锁
        self._cond = threading.Condition(threading.RLock())

    # ---------- 内部工具 ----------

    def _next_id(self, queue_id: str) -> str:
        """生成与 Redis Stream 同构的 ID，保证两种实现的 start_id 可以互换。"""
        now = int(time.time() * 1000)
        last_ms, last_seq = self._last_id.get(queue_id, (0, 0))
        new_id = (now, 0) if now > last_ms else (last_ms, last_seq + 1)
        self._last_id[queue_id] = new_id
        return f"{new_id[0]}-{new_id[1]}"

    def _drop(self, queue_id: str) -> None:
        """调用方必须已持有锁。"""
        self._sort_keys.pop(queue_id, None)
        self._items.pop(queue_id, None)
        self._done_flags.pop(queue_id, None)
        self._last_id.pop(queue_id, None)
        self._expire_at.pop(queue_id, None)

    def _purge_if_expired(self, queue_id: str) -> None:
        """调用方必须已持有锁。"""
        expire_at = self._expire_at.get(queue_id)
        if expire_at is not None and expire_at <= time.time():
            self._drop(queue_id)

    def _read_after(self, cursor: Tuple[int, int], queue_id: str) -> Tuple[List[Tuple[str, str]], bool]:
        """
        原子地返回 (游标之后的消息, 是否已结束)。

        两个值必须在同一次加锁内读取：生产者是先 produce 再 produce_done，
        所以只要读到 done=True，就说明所有消息在本次快照里已经全部可见，
        不存在"最后一条消息还没写进来就判定结束"的竞态。
        """
        with self._cond:
            self._purge_if_expired(queue_id)
            keys = self._sort_keys.get(queue_id)
            done = self._done_flags.get(queue_id, False)
            if not keys:
                return [], done
            start = bisect.bisect_right(keys, cursor)
            return list(self._items[queue_id][start:]), done

    def purge_expired(self) -> int:
        """惰性清理兜底：建议由定时任务周期调用，防止用户关页面后队列常驻内存。"""
        now = time.time()
        with self._cond:
            expired = [k for k, exp in self._expire_at.items() if exp <= now]
            for k in expired:
                self._drop(k)
            return len(expired)

    # ---------- 接口实现 ----------

    def exists(self, queue_id: str) -> bool:
        with self._cond:
            self._purge_if_expired(queue_id)
            return queue_id in self._items

    def produce(self, queue_id: str, message: Any, ttl: int = None) -> None:
        data = message if isinstance(message, str) else json.dumps(message, ensure_ascii=False)
        with self._cond:
            self._purge_if_expired(queue_id)
            if queue_id not in self._items:
                self._items[queue_id] = []
                self._sort_keys[queue_id] = []
            msg_id = self._next_id(queue_id)
            self._sort_keys[queue_id].append(parse_stream_id(msg_id))
            self._items[queue_id].append((msg_id, data))
            # 滑动过期，长会话不会中途被清掉
            self._expire_at[queue_id] = time.time() + (ttl or self._default_ttl)
            self._cond.notify_all()

    def produce_done(self, queue_id: str, ttl: int = None) -> None:
        with self._cond:
            self._done_flags[queue_id] = True
            self._expire_at[queue_id] = time.time() + (ttl or self._default_ttl)
            self._cond.notify_all()

    def is_done(self, queue_id: str) -> bool:
        with self._cond:
            return self._done_flags.get(queue_id, False)

    def consume(
            self,
            queue_id: str,
            start_id: str = "0",
            on_message: Optional[Callable[[str, str], None]] = None,
            on_done: Optional[Callable[[], None]] = None,
            timeout: float = 300,
            should_stop: Optional[Callable[[], bool]] = None,
    ) -> None:
        deadline = time.monotonic() + timeout
        cursor = parse_stream_id(start_id)
        try:
            while True:
                if should_stop is not None and should_stop():
                    break

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    maxkb_logger.warning(f"MessageQueue consume timeout: {queue_id}")
                    break

                batch, done = self._read_after(cursor, queue_id)
                if batch:
                    for msg_id, msg_data in batch:
                        if on_message:
                            on_message(msg_id, msg_data)
                        cursor = parse_stream_id(msg_id)
                    continue
                if done:
                    break

                # 等待生产者唤醒，而不是固定 sleep，降低首字延迟
                with self._cond:
                    self._cond.wait(min(0.05, remaining))
        finally:
            if on_done:
                on_done()

    def get_messages(self, queue_id: str, start_id: str = "0", count: int = 100) -> list:
        batch, _ = self._read_after(parse_stream_id(start_id), queue_id)
        return [{"id": mid, "data": data} for mid, data in batch[:count]]

    def delete(self, queue_id: str) -> None:
        with self._cond:
            self._drop(queue_id)
            self._cond.notify_all()

    def clear_by_pattern(self, pattern: str) -> int:
        with self._cond:
            keys = [k for k in self._items if fnmatch.fnmatch(k, pattern)]
            for k in keys:
                self._drop(k)
            self._cond.notify_all()
            return len(keys)


class RedisStreamMessageQueue(IMessageQueue):
    """
    Redis Stream 消息队列
    支持多消费者、断线重连、消息持久化
    """

    def __init__(self, namespace: str = "mq", redis_client=None, alias: str = "default"):
        self._namespace = namespace
        self._redis = redis_client
        self._alias = alias
        self._resolved = None
        self._default_ttl = DEFAULT_TTL
        self._batch_size = DEFAULT_BATCH_SIZE
        self._block_timeout = DEFAULT_BLOCK_TIMEOUT_MS
        self._block_limit = None

    # ---------- 连接 ----------

    def _resolve_redis(self):
        """
        django-redis 的 cache.client 是 DefaultClient 包装层，没有 xadd/xread，
        必须取出底层 redis-py 连接。
        """
        try:
            from django_redis import get_redis_connection
            return get_redis_connection(self._alias)
        except ImportError:
            pass
        except Exception as e:
            maxkb_logger.warning(f"get_redis_connection({self._alias}) failed: {e}")

        from django.core.cache import cache
        client = getattr(cache, "client", None)
        if client is not None and hasattr(client, "get_client"):
            return client.get_client(write=True)
        if client is not None and hasattr(client, "xadd"):
            return client
        raise MessageQueueError("当前 CACHES 后端不是 django-redis，无法使用 RedisStreamMessageQueue")

    def _get_redis(self):
        if self._redis is not None:
            return self._redis
        if self._resolved is None:
            self._resolved = self._resolve_redis()
        return self._resolved

    def ping(self) -> bool:
        """真实探活，不吞异常，供 create_message_queue 判断是否降级。"""
        return bool(self._get_redis().ping())

    def _block_limit_ms(self, redis) -> int:
        """
        XREAD 的 block 是让服务端挂起的时长，而客户端等响应用的是连接的 socket_timeout。
        一旦 block >= socket_timeout，空窗口必然先触发 "Timeout reading from socket"
        并导致 redis-py 断连重建。这里按连接实际配置反推一个安全上限。
        """
        if self._block_limit is not None:
            return self._block_limit

        limit = self._block_timeout
        try:
            kwargs = getattr(getattr(redis, "connection_pool", None), "connection_kwargs", None) or {}
            socket_timeout = kwargs.get("socket_timeout")
            if socket_timeout:
                safe = int(float(socket_timeout) * 1000 * BLOCK_SAFETY_RATIO)
                limit = max(100, min(limit, safe))
                if limit < self._block_timeout:
                    maxkb_logger.info(
                        f"MessageQueue: socket_timeout={socket_timeout}s，XREAD block 收敛到 {limit}ms"
                    )
        except Exception as e:
            maxkb_logger.warning(f"MessageQueue: 无法读取 socket_timeout，沿用默认 block: {e}")

        self._block_limit = limit
        return limit

    # ---------- 编解码 ----------

    def _key(self, queue_id: str) -> str:
        return f"{self._namespace}:{queue_id}"

    def _done_key(self, queue_id: str) -> str:
        return f"{self._namespace}:{queue_id}:done"

    def _encode(self, value: Any) -> str:
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    @staticmethod
    def _decode_bytes(data: Any) -> str:
        return data.decode("utf-8") if isinstance(data, (bytes, bytearray)) else str(data)

    def _decode_field(self, fields: dict, name: str = "data") -> str:
        """同时兼容 decode_responses=True / False 两种 client 配置。"""
        if not fields:
            return ""
        val = fields.get(name)
        if val is None:
            val = fields.get(name.encode("utf-8"))
        if val is None:
            return ""
        return self._decode_bytes(val)

    def _emit(self, messages, on_message) -> Optional[str]:
        last_id = None
        for msg_id_raw, fields in messages:
            msg_id = self._decode_bytes(msg_id_raw)
            if on_message:
                on_message(msg_id, self._decode_field(fields))
            last_id = msg_id
        return last_id

    # ---------- 接口实现 ----------

    def exists(self, queue_id: str) -> bool:
        try:
            return self._get_redis().exists(self._key(queue_id)) > 0
        except Exception as e:
            raise MessageQueueError(f"exists({queue_id}) failed: {e}") from e

    def produce(self, queue_id: str, message: Any, ttl: int = None) -> None:
        key = self._key(queue_id)
        try:
            # pipeline 合并 xadd + expire，流式场景每个 token 少一次 RTT；
            # 同时每次都续期，避免长会话中途整条 stream 过期
            pipe = self._get_redis().pipeline(transaction=False)
            pipe.xadd(key, {"data": self._encode(message)})
            pipe.expire(key, ttl or self._default_ttl)
            pipe.execute()
        except Exception as e:
            maxkb_logger.error(f"MessageQueue produce error [{queue_id}]: {e}")
            raise MessageQueueError(f"produce({queue_id}) failed: {e}") from e

    def produce_done(self, queue_id: str, ttl: int = None) -> None:
        try:
            self._get_redis().set(self._done_key(queue_id), "1", ex=ttl or self._default_ttl)
        except Exception as e:
            maxkb_logger.error(f"MessageQueue produce_done error [{queue_id}]: {e}")
            raise MessageQueueError(f"produce_done({queue_id}) failed: {e}") from e

    def is_done(self, queue_id: str) -> bool:
        try:
            return self._get_redis().exists(self._done_key(queue_id)) > 0
        except Exception as e:
            raise MessageQueueError(f"is_done({queue_id}) failed: {e}") from e

    def consume(
            self,
            queue_id: str,
            start_id: str = "0",
            on_message: Optional[Callable[[str, str], None]] = None,
            on_done: Optional[Callable[[], None]] = None,
            timeout: float = 300,
            should_stop: Optional[Callable[[], bool]] = None,
    ) -> None:
        key = self._key(queue_id)
        deadline = time.monotonic() + timeout
        current_id = start_id or "0"
        errors = 0

        try:
            redis = self._get_redis()
            while True:
                if should_stop is not None and should_stop():
                    break

                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    maxkb_logger.warning(f"MessageQueue consume timeout: {queue_id}")
                    break

                try:
                    # block 必须 >= 1：block=0 在 Redis 里是"无限阻塞"，会挂死消费线程
                    block_ms = max(1, min(int(remaining * 1000), self._block_limit_ms(redis)))
                    result = redis.xread({key: current_id}, count=self._batch_size, block=block_ms)
                    errors = 0
                except BENIGN_TIMEOUTS:
                    # 阻塞窗口内没有新消息而已，不是故障：不计入熔断预算，也不退避。
                    # 游标未推进，Stream 可重复读，不会丢消息。
                    result = None
                except Exception as e:
                    errors += 1
                    maxkb_logger.error(
                        f"MessageQueue consume error [{queue_id}] ({errors}/{MAX_CONSECUTIVE_ERRORS}): {e}"
                    )
                    if errors >= MAX_CONSECUTIVE_ERRORS:
                        break
                    time.sleep(min(0.1 * errors, 1.0))
                    continue

                if result:
                    for _, messages in result:
                        last_id = self._emit(messages, on_message)
                        if last_id:
                            current_id = last_id
                    continue

                # 阻塞窗口内没有新消息，检查是否已结束
                try:
                    finished = self.is_done(queue_id)
                except MessageQueueError:
                    continue
                if finished:
                    # done 标记是在所有 produce 之后写的，这里把尾部残留全部读干净
                    self._flush_remaining(redis, key, current_id, on_message)
                    break
        except MessageQueueError as e:
            maxkb_logger.error(f"MessageQueue consume aborted [{queue_id}]: {e}")
        finally:
            if on_done:
                on_done()

    def _flush_remaining(self, redis, key: str, current_id: str, on_message: Optional[Callable]) -> str:
        """
        用非阻塞 xread 循环读完尾部消息。
        不传 block 参数即为非阻塞，且 xread 天然是"ID 严格大于游标"的语义，
        无需依赖 Redis 6.2+ 的 "(" 排他区间写法。
        """
        cursor = current_id
        while True:
            try:
                result = redis.xread({key: cursor}, count=self._batch_size)
            except Exception as e:
                maxkb_logger.error(f"MessageQueue flush error [{key}]: {e}")
                break
            if not result:
                break
            total = 0
            for _, messages in result:
                total += len(messages)
                last_id = self._emit(messages, on_message)
                if last_id:
                    cursor = last_id
            if total < self._batch_size:
                break
        return cursor

    def get_messages(self, queue_id: str, start_id: str = "0", count: int = 100) -> list:
        try:
            result = self._get_redis().xread({self._key(queue_id): start_id or "0"}, count=count)
        except Exception as e:
            raise MessageQueueError(f"get_messages({queue_id}) failed: {e}") from e
        return [
            {"id": self._decode_bytes(mid), "data": self._decode_field(fields)}
            for _, messages in (result or [])
            for mid, fields in messages
        ]

    def delete(self, queue_id: str) -> None:
        try:
            self._get_redis().delete(self._key(queue_id), self._done_key(queue_id))
        except Exception as e:
            maxkb_logger.error(f"MessageQueue delete error [{queue_id}]: {e}")
            raise MessageQueueError(f"delete({queue_id}) failed: {e}") from e

    def clear_by_pattern(self, pattern: str) -> int:
        """返回删除的 stream 数量；对应的 :done 标记也会一并清理。"""
        try:
            redis = self._get_redis()
            count = 0
            for full_pattern, counted in (
                    (f"{self._namespace}:{pattern}", True),
                    (f"{self._namespace}:{pattern}:done", False),
            ):
                cursor = 0
                while True:
                    cursor, keys = redis.scan(cursor, match=full_pattern, count=500)
                    if keys:
                        redis.delete(*keys)
                        if counted:
                            count += len(keys)
                    if cursor == 0:
                        break
            return count
        except Exception as e:
            maxkb_logger.error(f"MessageQueue clear_by_pattern error [{pattern}]: {e}")
            return 0


def create_message_queue(namespace: str = "mq", use_redis: bool = True) -> IMessageQueue:
    """
    创建消息队列实例
    @param namespace: 命名空间
    @param use_redis: 是否使用Redis（False则使用内存实现）
    """
    if use_redis:
        try:
            queue = RedisStreamMessageQueue(namespace=namespace)
            queue.ping()
            return queue
        except Exception as e:
            maxkb_logger.warning(
                f"Redis 不可用，降级为 InMemoryMessageQueue（多 worker 部署下跨进程消费将失效）: {e}"
            )
    return InMemoryMessageQueue()


def get_message_queue(namespace: str = "chat") -> IMessageQueue:
    """进程内按 namespace 复用队列实例。禁止在业务代码里直接调 create_message_queue。"""
    instance = _instances.get(namespace)  # 快路径，GIL 下 dict.get 原子
    if instance is not None:
        return instance
    with _instances_lock:
        instance = _instances.get(namespace)  # 双检
        if instance is None:
            from django.conf import settings
            instance = create_message_queue(
                namespace=namespace,
                use_redis=getattr(settings, "MESSAGE_QUEUE_USE_REDIS", True),
            )
            _instances[namespace] = instance
        return instance
