# coding=utf-8
"""
@project: MaxKB
@file： ttv.py
@desc: 千帆视频生成模型（蒸汽机 Air，异步任务式接口 /video/generations）
"""

import time
from typing import ClassVar, Dict

import requests

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.base_ttv import BaseGenerationVideo


class QianfanVideoModel(MaxKBBaseModel, BaseGenerationVideo):
    api_key: str
    api_base: str
    model_name: str
    params: dict = {}

    REQUEST_TIMEOUT: ClassVar[tuple] = (10, 120)
    MAX_POLL_ATTEMPTS: ClassVar[int] = 180
    POLL_INTERVAL: ClassVar[int] = 5
    SUCCESS_STATUSES: ClassVar[frozenset] = frozenset({"succeeded"})
    FAIL_STATUSES: ClassVar[frozenset] = frozenset({"failed"})
    # 任务失败时用于提取错误信息的字段
    ERROR_KEYS: ClassVar[tuple] = ("error_msg", "error", "message", "msg", "detail", "description")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.api_base = kwargs.get("api_base")
        self.model_name = kwargs.get("model_name")
        self.params = kwargs.get("params", {}) or {}
        # 需要关闭默认的 Authorization 头污染
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {"params": {}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value
        return QianfanVideoModel(
            model_name=model_name,
            api_key=model_credential.get("api_key"),
            api_base=model_credential.get("api_base", "https://qianfan.baidubce.com/v2"),
            **optional_params,
        )

    def check_auth(self):
        return True

    def _base_url(self):
        """接口路径为 /video/generations（无 v2 前缀），去掉 api_base 末尾的 /v2。"""
        base = self.api_base.rstrip("/")
        if base.endswith("/v2"):
            base = base[:-3]
        return base.rstrip("/")

    def _request(self, method: str, url: str, **kwargs) -> dict:
        kwargs.setdefault("timeout", self.REQUEST_TIMEOUT)
        response = self._session.request(method, url, **kwargs)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            detail = e.response.text if e.response is not None else str(e)
            maxkb_logger.error(f"千帆视频接口请求失败: {detail}", exc_info=True)
            raise RuntimeError(f"HTTP 请求失败: {detail}") from e
        return response.json()

    @staticmethod
    def _extract_error(data: dict) -> str:
        for key in QianfanVideoModel.ERROR_KEYS:
            value = data.get(key)
            if value:
                return str(value)
        return str(data)

    def _wait_for_result(self, task_id: str) -> dict:
        query_url = f"{self._base_url()}/video/generations"
        for attempt in range(1, self.MAX_POLL_ATTEMPTS + 1):
            response_data = self._request("GET", query_url, params={"task_id": task_id})
            status = response_data.get("status")
            maxkb_logger.info(f"千帆视频任务状态 (尝试 {attempt}/{self.MAX_POLL_ATTEMPTS}): {status}")
            if status in self.SUCCESS_STATUSES:
                return response_data
            if status in self.FAIL_STATUSES:
                raise RuntimeError(f"视频生成失败: {self._extract_error(response_data)}")
            time.sleep(self.POLL_INTERVAL)
        raise RuntimeError(f"任务超时：经过 {self.MAX_POLL_ATTEMPTS} 次轮询后仍未完成")

    def generate_video(self, prompt, negative_prompt=None, first_frame_url=None, last_frame_url=None, **kwargs):
        content = [{"type": "text", "text": prompt}]
        if first_frame_url:
            content.append({"type": "image_url", "image_url": {"url": first_frame_url}})
        if not any(item.get("type") == "image_url" for item in content):
            # 图生视频（musesteamer-air-i2v）必须包含图片信息
            maxkb_logger.warning("千帆视频生成：未提供图片，文生视频接口可能不支持该模型")

        payload = {"model": self.model_name, "content": content}
        payload.update(self.params)

        maxkb_logger.info(f"提交千帆视频生成任务，模型: {self.model_name}")
        response_data = self._request("POST", f"{self._base_url()}/video/generations", json=payload)

        task_id = response_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"提交任务失败，未获取到 task_id: {response_data}")

        response_data = self._wait_for_result(task_id)

        video_url = (response_data.get("content") or {}).get("video_url")
        if not video_url:
            raise RuntimeError(f"任务成功但未获取到 video_url: {response_data}")
        return video_url
