# coding=utf-8
import time
from typing import Dict, Optional

import requests

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.base_ttv import BaseGenerationVideo


class GenerationVideoModel(MaxKBBaseModel, BaseGenerationVideo):
    """MiniMax 视频生成模型，兼容 V1 与 V2 (MiniMax-H3) 两套接口。"""

    api_key: str
    api_base: str
    model_name: str
    params: dict
    max_retries: int = 3
    retry_delay: int = 10  # 秒

    DEFAULT_API_BASE = "https://api.minimaxi.com/v1"
    REQUEST_TIMEOUT = (10, 120)  # (连接超时, 读取超时)
    MAX_POLL_ATTEMPTS = 60  # 最多轮询 60 次（约 10 分钟）

    # V2 (MiniMax-H3) 专用参数
    V2_EXTRA_FIELDS = ("resolution", "duration", "ratio", "callback_url")
    SUCCESS_STATUSES = frozenset({"succeeded", "Success"})
    FAIL_STATUSES = frozenset({"failed", "Fail", "cancelled", "Cancel"})
    ERROR_KEYS = ("error_message", "error", "detail", "message", "msg")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.api_base = kwargs.get("api_base", self.DEFAULT_API_BASE)
        self.model_name = kwargs.get("model_name")
        self.params = kwargs.get("params", {}) or {}
        self.max_retries = kwargs.get("max_retries", 3)
        self.retry_delay = kwargs.get("retry_delay", 10)
        # 显式参数可覆盖自动探测（params.api_version: 'v1' / 'v2'）
        self.api_version = self.params.get("api_version", "auto")
        self._session = self._build_session()

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {"params": {}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value

        api_base = model_credential.get("api_base", "https://api.minimaxi.com/v1")

        return GenerationVideoModel(
            model_name=model_name,
            api_key=model_credential.get("api_key"),
            api_base=api_base,
            **optional_params,
        )

    def check_auth(self):
        return True

    def _build_session(self) -> requests.Session:
        """创建带鉴权头与连接复用的请求会话。"""
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        return session

    # ---------- API 版本探测 / URL 构建 ----------

    def _detect_api_version(self) -> str:
        """探测当前使用 V1 还是 V2 (MiniMax-H3)。"""
        if self.api_version in ("v1", "v2"):
            return self.api_version
        # 模型名包含 H3 -> V2
        if self.model_name and "H3" in self.model_name.upper():
            return "v2"
        # api_base 路径包含 /v2 -> V2
        base_path = self.api_base.split("://", 1)[-1] if "://" in self.api_base else self.api_base
        if "/v2" in base_path:
            return "v2"
        return "v1"

    def _base_url(self) -> str:
        """去掉结尾的 /v1 或 /v2，返回纯净 base，便于拼装两套路径。"""
        base = self.api_base.rstrip("/")
        if base.endswith("/v1") or base.endswith("/v2"):
            base = base[:-3]
        return base.rstrip("/")

    def _v2(self) -> bool:
        return self._detect_api_version() == "v2"

    # ---------- 底层请求 / 轮询 ----------

    def _request(self, method: str, url: str, **kwargs) -> dict:
        """带固定间隔重试的请求封装，成功返回 JSON 响应。"""
        kwargs.setdefault("timeout", self.REQUEST_TIMEOUT)
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self._session.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
            except (
                requests.exceptions.ProxyError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
            ) as exc:
                if attempt < self.max_retries:
                    maxkb_logger.warning(f"网络错误: {exc}，正在重试 {attempt + 1}/{self.max_retries}...")
                    time.sleep(self.retry_delay)
                else:
                    raise RuntimeError("多次重试后仍无法连接到 MiniMax API，请检查代理或网络配置") from exc
            except requests.exceptions.HTTPError as exc:
                detail = exc.response.text if exc.response is not None else str(exc)
                raise RuntimeError(f"HTTP 请求失败: {detail}") from exc
        raise RuntimeError("多次重试后仍无法连接到 MiniMax API，请检查代理或网络配置")

    def _wait_for_result(self, query_url: str, task_id: Optional[str] = None) -> dict:
        """轮询任务状态直至成功/失败，成功时返回原始响应。"""
        params = {"task_id": task_id} if task_id else None
        for attempt in range(1, self.MAX_POLL_ATTEMPTS + 1):
            response_data = self._request("GET", query_url, params=params)
            task = response_data.get("task") or response_data
            status = task.get("status")

            maxkb_logger.info(f"当前任务状态 (尝试 {attempt}/{self.MAX_POLL_ATTEMPTS}): {status}")

            if status in self.SUCCESS_STATUSES:
                return response_data
            if status in self.FAIL_STATUSES:
                error_msg = self._extract_error(task, response_data)
                raise RuntimeError(f"视频生成失败: {error_msg}")
            # queued / running 等状态，继续轮询
            time.sleep(self.retry_delay)

        raise RuntimeError(f"任务超时：经过 {self.MAX_POLL_ATTEMPTS} 次轮询后仍未完成")

    @staticmethod
    def _extract_error(task: dict, response_data: dict) -> str:
        for container in (task, response_data):
            if not isinstance(container, dict):
                continue
            for key in GenerationVideoModel.ERROR_KEYS:
                value = container.get(key)
                if value:
                    return str(value)
        return "未知错误"

    # ---------- 对外入口 ----------

    def generate_video(self, prompt, negative_prompt=None, first_frame_url=None, last_frame_url=None, **kwargs):
        """
        生成视频。
        prompt: 文本描述
        negative_prompt: 反向文本描述（MiniMax 暂不支持，保留参数以兼容接口）
        first_frame_url: 起始关键帧图片 URL (图生视频或首尾帧模式)
        last_frame_url: 结束关键帧图片 URL (首尾帧模式)

        返回: 视频下载 URL
        """
        # 自动兼容 V1 / V2 (MiniMax-H3) 两套参数逻辑
        if self._v2():
            return self._generate_video_v2(prompt, first_frame_url, last_frame_url, **kwargs)
        return self._generate_video_v1(prompt, first_frame_url, last_frame_url, **kwargs)

    # ---------- V2 (MiniMax-H3) 流程 ----------

    def _build_v2_payload(self, prompt, first_frame_url, last_frame_url) -> dict:
        content = [{"type": "text", "text": prompt}]
        if first_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": first_frame_url},
                    "role": "first_frame",
                }
            )
        if last_frame_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": last_frame_url},
                    "role": "last_frame",
                }
            )

        payload = {"model": self.model_name, "content": content}
        # V2 必需的 resolution / duration，以及可选的 ratio / callback_url 均来自 params
        for key in self.V2_EXTRA_FIELDS:
            if key in self.params:
                payload[key] = self.params[key]
        return payload

    def _generate_video_v2(self, prompt, first_frame_url=None, last_frame_url=None, **kwargs) -> str:
        base_url = f"{self._base_url()}/v2/video_generation"
        payload = self._build_v2_payload(prompt, first_frame_url, last_frame_url)

        maxkb_logger.info(f"提交视频生成任务(V2/H3)，模型: {self.model_name}")
        response_data = self._request("POST", base_url, json=payload)

        task_id = response_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"提交任务失败，未获取到 task_id: {response_data}")

        query_url = f"{self._base_url()}/v2/query/video_generation/{task_id}"
        response_data = self._wait_for_result(query_url)

        task = response_data.get("task") or response_data
        video_url = (task.get("content") or {}).get("url")
        if not video_url:
            raise RuntimeError(f"任务成功但未获取到视频 URL: {response_data}")
        return video_url

    # ---------- V1 流程（兼容老接口） ----------

    def _generate_video_v1(self, prompt, first_frame_url=None, last_frame_url=None, **kwargs) -> str:
        base_url = f"{self._base_url()}/v1/video_generation"

        payload = {"prompt": prompt, "model": self.model_name}
        # 根据提供的参数判断生成模式
        if first_frame_url and last_frame_url:
            payload.update(first_frame_image=first_frame_url, last_frame_image=last_frame_url)
        elif first_frame_url:
            payload["first_frame_image"] = first_frame_url

        # 合并额外参数（duration, resolution 等），跳过版本探测专用字段
        payload.update({k: v for k, v in self.params.items() if k != "api_version"})

        maxkb_logger.info(f"提交视频生成任务(V1)，模型: {self.model_name}")
        response_data = self._request("POST", base_url, json=payload)

        task_id = response_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"提交任务失败，未获取到 task_id: {response_data}")

        query_url = f"{self._base_url()}/v1/query/video_generation"
        response_data = self._wait_for_result(query_url, task_id=task_id)

        file_id = response_data.get("file_id")
        if not file_id:
            raise RuntimeError(f"任务成功但未获取到 file_id: {response_data}")
        return self._get_video_download_url_v1(file_id)

    def _get_video_download_url_v1(self, file_id: str) -> str:
        """根据 file_id 获取视频下载链接（V1）。"""
        retrieve_url = f"{self._base_url()}/v1/files/retrieve"
        response_data = self._request("GET", retrieve_url, params={"file_id": file_id})

        download_url = (response_data.get("file") or {}).get("download_url")
        if not download_url:
            raise RuntimeError(f"获取下载链接失败: {response_data}")
        return download_url
