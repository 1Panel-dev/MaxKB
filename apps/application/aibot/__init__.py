"""
企业微信智能机器人 Python SDK

基于 WebSocket 长连接通道，提供消息收发、流式回复、模板卡片、事件回调、文件下载解密等核心能力。
"""

__version__ = "1.0.0"

from .api import WeComApiClient
from .client import WSClient
from .crypto_utils import decrypt_file
from .logger import DefaultLogger
from .message_handler import MessageHandler
from .types import (
    MessageType,
    MediaType,
    EventType,
    TemplateCardType,
    WsCmd,
    WSClientOptions,
    WsFrame,
    WsFrameHeaders,
    Logger,
)
from .utils import generate_req_id, generate_random_string
from .ws import WsConnectionManager

__all__ = [
    # 版本
    "__version__",
    # 类
    "WSClient",
    "WeComApiClient",
    "WsConnectionManager",
    "MessageHandler",
    "DefaultLogger",
    # 函数
    "decrypt_file",
    "generate_req_id",
    "generate_random_string",
    # 枚举/常量
    "MediaType",
    "MessageType",
    "EventType",
    "TemplateCardType",
    "WsCmd",
    # 类型
    "WSClientOptions",
    "WsFrame",
    "WsFrameHeaders",
    "Logger",
]
