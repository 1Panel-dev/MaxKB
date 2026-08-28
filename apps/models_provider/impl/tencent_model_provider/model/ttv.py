# coding=utf-8

import time
from typing import ClassVar, Dict

import requests

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.base_ttv import BaseGenerationVideo


class TencentVideoModel(MaxKBBaseModel, BaseGenerationVideo):
    """腾讯混元/优图视频生成模型（TokenHub OpenAI 兼容视频接口）。

    同时兼容文生视频（HY-Video-1.5）与图生视频/首尾帧（YT-Video-2.0）：
    - 提交任务：POST /v1/api/video/submit
    - 查询任务：POST /v1/api/video/query
    """

    DEFAULT_BASE_URL: ClassVar[str] = "https://tokenhub.tencentmaas.com/v1"
    REQUEST_TIMEOUT: ClassVar[tuple] = (10, 120)  # (连接超时, 读取超时)
    MAX_POLL_ATTEMPTS: ClassVar[int] = 120  # 最多轮询 120 次（约 6 分钟）
    POLL_INTERVAL: ClassVar[int] = 3  # 秒
    COMPLETED_STATUS: ClassVar[str] = "completed"
    FAILED_STATUSES: ClassVar[frozenset] = frozenset({"failed", "error", "cancelled", "canceled"})

    api_key: str
    model_name: str
    params: dict = {}
    base_url: str = DEFAULT_BASE_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.model_name = kwargs.get("model_name")
        self.params = kwargs.get("params") or {}
        self.base_url = (kwargs.get("base_url") or self.DEFAULT_BASE_URL).rstrip("/")

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(
        model_type: str, model_name: str, model_credential: Dict[str, object], **model_kwargs
    ) -> "TencentVideoModel":
        optional_params = {"params": {}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value
        return TencentVideoModel(
            api_key=model_credential.get("api_key"),
            model_name=model_name,
            base_url=model_credential.get("base_url") or TencentVideoModel.DEFAULT_BASE_URL,
            **optional_params,
        )

    def _endpoints(self) -> tuple:
        """根据 base_url 推导 submit/query 地址。

        base_url 可以是根地址（如 https://tokenhub.tencentmaas.com/v1），
        也可以是完整的 submit 或 query 地址，均能正确推导出两个接口地址。
        """
        base = self.base_url.rstrip("/")
        if "/api/video/submit" in base:
            submit = base
            query = base[: base.index("/api/video/submit")] + "/api/video/query"
        elif "/api/video/query" in base:
            query = base
            submit = base[: base.index("/api/video/query")] + "/api/video/submit"
        else:
            submit = f"{base}/api/video/submit"
            query = f"{base}/api/video/query"
        return submit, query

    @property
    def submit_url(self) -> str:
        return self._endpoints()[0]

    @property
    def query_url(self) -> str:
        return self._endpoints()[1]

    def check_auth(self):
        if not self.api_key:
            raise RuntimeError("api_key is required")
        return True

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    def _build_payload(self, prompt: str, first_frame_url=None, last_frame_url=None) -> dict:
        payload = {"model": self.model_name, "prompt": prompt}
        # 图生视频/首尾帧模式：优先使用首帧，其次使用尾帧作为输入图片
        image_url = first_frame_url or last_frame_url
        if image_url:
            payload["image"] = {"url": image_url}
        # 合并模型参数（resolution、fps、logo_add 等），过滤空值
        for key, value in self.params.items():
            if value not in (None, ""):
                payload[key] = value
        return payload

    def _submit(self, prompt: str, first_frame_url=None, last_frame_url=None):
        payload = self._build_payload(prompt, first_frame_url, last_frame_url)
        maxkb_logger.info(f"提交腾讯视频生成任务，模型: {self.model_name}, url: {self.submit_url}")
        response = requests.post(self.submit_url, headers=self._headers(), json=payload, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        result = response.json()
        task_id = result.get("id")
        if not task_id:
            raise RuntimeError(f"腾讯视频提交任务失败，未获取到 id: {result}")
        return task_id, result.get("status")

    def _query(self, task_id: str) -> dict:
        payload = {"model": self.model_name, "id": task_id}
        response = requests.post(self.query_url, headers=self._headers(), json=payload, timeout=self.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _wait_for_result(self, task_id: str) -> dict:
        for attempt in range(1, self.MAX_POLL_ATTEMPTS + 1):
            result = self._query(task_id)
            status = result.get("status")
            maxkb_logger.info(
                f"查询腾讯视频任务 {task_id} 状态: {status}, 进度: {result.get('progress')}, 第 {attempt} 次"
            )
            if status == self.COMPLETED_STATUS:
                return result
            if status in self.FAILED_STATUSES:
                message = (
                    result.get("message")
                    or result.get("error_message")
                    or result.get("error")
                    or result.get("msg")
                    or "未知错误"
                )
                raise RuntimeError(f"腾讯视频任务 {task_id} 执行失败: {message}")
            time.sleep(self.POLL_INTERVAL)
        raise RuntimeError(f"腾讯视频任务 {task_id} 轮询超时（{self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL} 秒）")

    def generate_video(
        self, prompt: str, negative_prompt: str = None, first_frame_url=None, last_frame_url=None, **kwargs
    ):
        task_id, _ = self._submit(prompt, first_frame_url, last_frame_url)
        result = self._wait_for_result(task_id)
        data = result.get("data") or {}
        video_url = data.get("url")
        if not video_url:
            raise RuntimeError(f"腾讯视频任务完成但未获取到视频 URL: {result}")
        return video_url
