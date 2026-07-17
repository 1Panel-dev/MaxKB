"""
WSClient 核心客户端

对标 Node.js SDK src/client.ts
继承自 pyee.AsyncIOEventEmitter，组合 WsConnectionManager + MessageHandler + WeComApiClient。
"""

import asyncio
import base64
import hashlib
import math
from typing import Any, Dict, List, Optional, Tuple, Union

from pyee.asyncio import AsyncIOEventEmitter

from .api import WeComApiClient
from .crypto_utils import decrypt_file
from .logger import DefaultLogger
from .message_handler import MessageHandler
from .types import MediaType, WsCmd, WsFrame, WsFrameHeaders, WSClientOptions
from .utils import generate_req_id
from .ws import WsConnectionManager


class WSClient(AsyncIOEventEmitter):
    """
    企业微信智能机器人 Python SDK 核心客户端

    基于 asyncio + pyee 的事件驱动架构，提供 WebSocket 长连接消息收发能力。
    """

    def __init__(self, options: WSClientOptions) -> None:
        super().__init__()

        self._options = options
        self._logger = options.logger or DefaultLogger()
        self._started = False

        # 初始化 API 客户端（仅用于文件下载）
        self._api_client = WeComApiClient(
            self._logger,
            self._options.request_timeout,
        )

        # 初始化 WebSocket 管理器
        self._ws_manager = WsConnectionManager(
            self._logger,
            heartbeat_interval=self._options.heartbeat_interval,
            reconnect_base_delay=self._options.reconnect_interval,
            max_reconnect_attempts=self._options.max_reconnect_attempts,
            ws_url=self._options.ws_url or None,
        )

        # 设置认证凭证
        self._ws_manager.set_credentials(self._options.bot_id, self._options.secret)

        # 初始化消息处理器
        self._message_handler = MessageHandler(self._logger)

        # 绑定 WebSocket 事件
        self._setup_ws_events()

    def _setup_ws_events(self) -> None:
        """设置 WebSocket 事件处理"""
        self._ws_manager.on_connected = lambda: self.emit("connected")

        def _on_authenticated() -> None:
            self._logger.info("Authenticated")
            self.emit("authenticated")

        self._ws_manager.on_authenticated = _on_authenticated

        self._ws_manager.on_disconnected = lambda reason: self.emit(
            "disconnected", reason
        )
        self._ws_manager.on_reconnecting = lambda attempt: self.emit(
            "reconnecting", attempt
        )
        self._ws_manager.on_error = lambda error: self.emit("error", error)
        self._ws_manager.on_message = lambda frame: self._message_handler.handle_frame(
            frame, self
        )

    async def connect(self) -> "WSClient":
        """
        建立 WebSocket 长连接

        SDK 使用内置默认地址建立连接，连接成功后自动发送认证帧（bot_id + secret）。

        :return: 返回 self，支持链式调用
        """
        if self._started:
            self._logger.warn("Client already connected")
            return self

        self._logger.info("Establishing WebSocket connection...")
        self._started = True

        await self._ws_manager.connect()

        return self

    def disconnect(self) -> None:
        """断开 WebSocket 连接"""
        if not self._started:
            self._logger.warn("Client not connected")
            return

        self._logger.info("Disconnecting...")
        self._started = False
        self._ws_manager.disconnect()
        self._logger.info("Disconnected")

    async def reply(
            self,
            frame: WsFrameHeaders,
            body: Dict[str, Any],
            cmd: Optional[str] = None,
    ) -> WsFrame:
        """
        通过 WebSocket 通道发送回复消息（通用方法）

        :param frame: 收到的原始 WebSocket 帧，透传 headers.req_id
        :param body: 回复消息体
        :param cmd: 发送的命令类型
        :return: 回执帧
        """
        headers = frame.get("headers", {})
        req_id = headers.get("req_id", "")
        return await self._ws_manager.send_reply(req_id, body, cmd or WsCmd.RESPONSE)

    async def reply_stream(
            self,
            frame: WsFrameHeaders,
            stream_id: str,
            content: str,
            finish: bool = False,
            msg_item: Optional[List[Dict[str, Any]]] = None,
            feedback: Optional[Dict[str, Any]] = None,
    ) -> WsFrame:
        """
        发送流式文本回复（便捷方法）

        :param frame: 收到的原始 WebSocket 帧，透传 headers.req_id
        :param stream_id: 流式消息 ID
        :param content: 回复内容（支持 Markdown）
        :param finish: 是否结束流式消息，默认 False
        :param msg_item: 图文混排项（仅在 finish=True 时有效）
        :param feedback: 反馈信息（仅在首次回复时设置）
        :return: 回执帧
        """
        stream: Dict[str, Any] = {
            "id": stream_id,
            "finish": finish,
            "content": content,
        }

        # msg_item 仅在 finish=True 时支持
        if finish and msg_item and len(msg_item) > 0:
            stream["msg_item"] = msg_item

        # feedback 仅在首次回复时设置
        if feedback:
            stream["feedback"] = feedback

        return await self.reply(
            frame,
            {
                "msgtype": "stream",
                "stream": stream,
            },
        )

    async def reply_welcome(
            self,
            frame: WsFrameHeaders,
            body: Dict[str, Any],
    ) -> WsFrame:
        """
        发送欢迎语回复

        注意：此方法需要使用对应事件（如 enter_chat）的 req_id 才能调用。
        收到事件回调后需在 5 秒内发送回复，超时将无法发送欢迎语。

        :param frame: 对应事件的 WebSocket 帧
        :param body: 欢迎语消息体（支持文本或模板卡片格式）
        :return: 回执帧
        """
        return await self.reply(frame, body, WsCmd.RESPONSE_WELCOME)

    async def reply_template_card(
            self,
            frame: WsFrameHeaders,
            template_card: Dict[str, Any],
            feedback: Optional[Dict[str, Any]] = None,
    ) -> WsFrame:
        """
        回复模板卡片消息

        :param frame: 收到的原始 WebSocket 帧
        :param template_card: 模板卡片内容
        :param feedback: 反馈信息
        :return: 回执帧
        """
        card = {**template_card, "feedback": feedback} if feedback else template_card
        body = {
            "msgtype": "template_card",
            "template_card": card,
        }
        return await self.reply(frame, body)

    async def reply_stream_with_card(
            self,
            frame: WsFrameHeaders,
            stream_id: str,
            content: str,
            finish: bool = False,
            msg_item: Optional[List[Dict[str, Any]]] = None,
            stream_feedback: Optional[Dict[str, Any]] = None,
            template_card: Optional[Dict[str, Any]] = None,
            card_feedback: Optional[Dict[str, Any]] = None,
    ) -> WsFrame:
        """
        发送流式消息 + 模板卡片组合回复

        :param frame: 收到的原始 WebSocket 帧
        :param stream_id: 流式消息 ID
        :param content: 回复内容（支持 Markdown）
        :param finish: 是否结束流式消息，默认 False
        :param msg_item: 图文混排项（仅在 finish=True 时有效）
        :param stream_feedback: 流式消息反馈信息（首次回复时设置）
        :param template_card: 模板卡片内容（同一消息只能回复一次）
        :param card_feedback: 模板卡片反馈信息
        :return: 回执帧
        """
        stream: Dict[str, Any] = {
            "id": stream_id,
            "finish": finish,
            "content": content,
        }

        if finish and msg_item and len(msg_item) > 0:
            stream["msg_item"] = msg_item

        if stream_feedback:
            stream["feedback"] = stream_feedback

        body: Dict[str, Any] = {
            "msgtype": "stream_with_template_card",
            "stream": stream,
        }

        if template_card:
            card = (
                {**template_card, "feedback": card_feedback}
                if card_feedback
                else template_card
            )
            body["template_card"] = card

        return await self.reply(frame, body)

    async def update_template_card(
            self,
            frame: WsFrameHeaders,
            template_card: Dict[str, Any],
            userids: Optional[List[str]] = None,
    ) -> WsFrame:
        """
        更新模板卡片

        注意：此方法需要使用对应事件（template_card_event）的 req_id 才能调用。
        收到事件回调后需在 5 秒内发送回复，超时将无法更新卡片。

        :param frame: 对应事件的 WebSocket 帧
        :param template_card: 模板卡片内容（task_id 需跟回调收到的 task_id 一致）
        :param userids: 要替换模版卡片消息的 userid 列表
        :return: 回执帧
        """
        body: Dict[str, Any] = {
            "response_type": "update_template_card",
            "template_card": template_card,
        }
        if userids and len(userids) > 0:
            body["userids"] = userids

        return await self.reply(frame, body, WsCmd.RESPONSE_UPDATE)

    async def send_message(
            self,
            chatid: str,
            body: Dict[str, Any],
    ) -> WsFrame:
        """
        主动发送消息

        向指定会话（单聊或群聊）主动推送消息，无需依赖收到的回调帧。

        :param chatid: 会话 ID，单聊填用户的 userid，群聊填对应群聊的 chatid
        :param body: 消息体（支持 markdown 或 template_card 格式）
        :return: 回执帧
        """
        req_id = generate_req_id(WsCmd.SEND_MSG)
        full_body = {"chatid": chatid, **body}
        return await self._ws_manager.send_reply(req_id, full_body, WsCmd.SEND_MSG)

    async def download_file(
            self, url: str, aes_key: Optional[str] = None
    ) -> Tuple[bytes, Optional[str]]:
        """
        下载文件并使用 AES 密钥解密

        :param url: 文件下载地址
        :param aes_key: AES 解密密钥（Base64 编码），取自消息中 image.aeskey 或 file.aeskey
        :return: (解密后的文件数据, 文件名)
        """
        self._logger.info("Downloading and decrypting file...")

        try:
            # 下载加密的文件数据
            encrypted_data, filename = await self._api_client.download_file_raw(url)

            # 如果没有提供 aes_key，直接返回原始数据
            if not aes_key:
                self._logger.warn("No aes_key provided, returning raw file data")
                return encrypted_data, filename

            # 使用独立的解密模块进行 AES-256-CBC 解密
            decrypted_data = decrypt_file(encrypted_data, aes_key)

            self._logger.info("File downloaded and decrypted successfully")
            return decrypted_data, filename

        except Exception as e:
            self._logger.error(f"File download/decrypt failed: {e}")
            raise

    async def upload_media(
            self,
            data: bytes,
            filename: str,
            media_type: Union[MediaType, str],
            md5: Optional[str] = None,
    ) -> str:
        """
        上传临时素材，返回 media_id（有效期 3 天）

        采用分片方式上传（每片 ≤512 KB，Base64 编码），流程：
          1. aibot_upload_media_init  → upload_id
          2. aibot_upload_media_chunk × N
          3. aibot_upload_media_finish → media_id

        文件大小限制：image/voice ≤2MB，video ≤10MB，file ≤20MB
        上传频率限制：≤30次/分钟，≤1000次/小时

        :param data: 文件原始字节
        :param filename: 文件名（含扩展名），不超过 256 字节
        :param media_type: 文件类型，使用 MediaType 枚举或对应字符串
        :param md5: 可选，文件 MD5（十六进制字符串），服务端将在合并后校验
        :return: media_id 字符串
        :raises ValueError: 文件大小超出分片限制
        :raises RuntimeError: 上传过程中服务端返回错误
        """
        # 每片原始字节上限（Base64 编码前）
        chunk_size = 512 * 1024  # 512 KB
        total_size = len(data)
        total_chunks = math.ceil(total_size / chunk_size) if total_size > 0 else 1

        if total_chunks > 100:
            raise ValueError(
                f"upload_media: file too large, requires {total_chunks} chunks "
                f"(max 100). Max sizes: image/voice 2MB, video 10MB, file 20MB."
            )

        # 如果调用方未传 md5，自动计算
        file_md5 = md5 or hashlib.md5(data).hexdigest()

        self._logger.info(
            f"Uploading media: filename={filename}, type={media_type}, "
            f"size={total_size}B, chunks={total_chunks}"
        )

        # ── Step 1: 初始化上传 ───────────────────────────────────────────
        init_req_id = generate_req_id(WsCmd.UPLOAD_MEDIA_INIT)
        init_body: Dict[str, Any] = {
            "type": media_type.value if isinstance(media_type, MediaType) else media_type,
            "filename": filename,
            "total_size": total_size,
            "total_chunks": total_chunks,
            "md5": file_md5,
        }
        init_frame = await self._ws_manager.send_reply(
            init_req_id, init_body, WsCmd.UPLOAD_MEDIA_INIT
        )
        upload_id: str = init_frame.get("body", {}).get("upload_id", "")
        if not upload_id:
            raise RuntimeError(
                f"upload_media: init failed, no upload_id in response: {init_frame}"
            )
        self._logger.debug(f"upload_media: got upload_id={upload_id}")

        # ── Step 2: 逐片上传 ─────────────────────────────────────────────
        for i in range(total_chunks):
            chunk_data = data[i * chunk_size: (i + 1) * chunk_size]
            chunk_b64 = base64.b64encode(chunk_data).decode("ascii")
            chunk_req_id = generate_req_id(WsCmd.UPLOAD_MEDIA_CHUNK)
            chunk_body: Dict[str, Any] = {
                "upload_id": upload_id,
                "chunk_index": i,
                "base64_data": chunk_b64,
            }
            await self._ws_manager.send_reply(
                chunk_req_id, chunk_body, WsCmd.UPLOAD_MEDIA_CHUNK
            )
            self._logger.debug(f"upload_media: chunk {i + 1}/{total_chunks} uploaded")

        # ── Step 3: 完成上传 ─────────────────────────────────────────────
        finish_req_id = generate_req_id(WsCmd.UPLOAD_MEDIA_FINISH)
        finish_body: Dict[str, Any] = {"upload_id": upload_id}
        finish_frame = await self._ws_manager.send_reply(
            finish_req_id, finish_body, WsCmd.UPLOAD_MEDIA_FINISH
        )
        media_id: str = finish_frame.get("body", {}).get("media_id", "")
        if not media_id:
            raise RuntimeError(
                f"upload_media: finish failed, no media_id in response: {finish_frame}"
            )

        self._logger.info(f"upload_media: done, media_id={media_id}")
        return media_id

    async def reply_image(
            self,
            frame: WsFrameHeaders,
            media_id: str,
    ) -> WsFrame:
        """
        回复图片消息

        :param frame: 收到的原始 WebSocket 帧
        :param media_id: 图片的 media_id，由 upload_media() 获取
        :return: 回执帧
        """
        return await self.reply(
            frame,
            {"msgtype": "image", "image": {"media_id": media_id}},
        )

    async def reply_file(
            self,
            frame: WsFrameHeaders,
            media_id: str,
    ) -> WsFrame:
        """
        回复文件消息

        :param frame: 收到的原始 WebSocket 帧
        :param media_id: 文件的 media_id，由 upload_media() 获取
        :return: 回执帧
        """
        return await self.reply(
            frame,
            {"msgtype": "file", "file": {"media_id": media_id}},
        )

    async def reply_voice(
            self,
            frame: WsFrameHeaders,
            media_id: str,
    ) -> WsFrame:
        """
        回复语音消息

        :param frame: 收到的原始 WebSocket 帧
        :param media_id: 语音的 media_id，由 upload_media() 获取
        :return: 回执帧
        """
        return await self.reply(
            frame,
            {"msgtype": "voice", "voice": {"media_id": media_id}},
        )

    async def reply_video(
            self,
            frame: WsFrameHeaders,
            media_id: str,
            title: Optional[str] = None,
            description: Optional[str] = None,
    ) -> WsFrame:
        """
        回复视频消息

        :param frame: 收到的原始 WebSocket 帧
        :param media_id: 视频的 media_id，由 upload_media() 获取
        :param title: 可选，视频标题，不超过 64 字节
        :param description: 可选，视频描述，不超过 512 字节
        :return: 回执帧
        """
        video: Dict[str, Any] = {"media_id": media_id}
        if title:
            video["title"] = title
        if description:
            video["description"] = description
        return await self.reply(
            frame,
            {"msgtype": "video", "video": video},
        )

    @property
    def is_connected(self) -> bool:
        """获取当前连接状态"""
        return self._ws_manager.is_connected

    @property
    def api(self) -> WeComApiClient:
        """获取 API 客户端实例（供高级用途使用）"""
        return self._api_client

    def run(self) -> None:
        """
        便捷方法：启动事件循环并连接

        等价于:
            asyncio.get_event_loop().run_until_complete(client.connect())
            asyncio.get_event_loop().run_forever()
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self.connect())
            loop.run_forever()
        except KeyboardInterrupt:
            self.disconnect()
        finally:
            loop.close()
