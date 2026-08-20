import time
from typing import Dict

import requests

from common.utils.logger import maxkb_logger
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.base_ttv import BaseGenerationVideo


class GenerationVideoModel(MaxKBBaseModel, BaseGenerationVideo):
    api_key: str
    api_base: str
    model_name: str
    params: dict
    max_retries: int = 3
    retry_delay: int = 10  # seconds

    # V2 (MiniMax-H3) 专用参数
    v2_extra_fields = ("resolution", "duration", "ratio", "callback_url")
    # V2 完成 / 失败状态
    v2_success_status = ("succeeded", "Success")
    v2_fail_status = ("failed", "Fail", "cancelled", "Cancel")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base', 'https://api.minimaxi.com/v1')
        self.model_name = kwargs.get('model_name')
        self.params = kwargs.get('params', {}) or {}
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = kwargs.get('retry_delay', 10)
        # 显式参数可覆盖自动探测（params.api_version: 'v1' / 'v2'）
        self.api_version = self.params.get('api_version', 'auto')

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value

        api_base = model_credential.get('api_base', 'https://api.minimaxi.com/v1')

        return GenerationVideoModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            api_base=api_base,
            **optional_params,
        )

    def check_auth(self):
        return True

    # ---------- API 版本探测 / URL 构建 ----------

    def _detect_api_version(self) -> str:
        """探测当前使用 V1 还是 V2 (MiniMax-H3)。"""
        if self.api_version in ('v1', 'v2'):
            return self.api_version
        # 模型名包含 H3 -> V2
        if self.model_name and 'H3' in self.model_name.upper():
            return 'v2'
        # api_base 路径包含 /v2 -> V2
        base_path = self.api_base.split('://', 1)[-1] if '://' in self.api_base else self.api_base
        if '/v2' in base_path:
            return 'v2'
        return 'v1'

    def _base_url(self) -> str:
        """去掉结尾的 /v1 或 /v2，返回纯净 base，便于拼装两套路径。"""
        base = self.api_base.rstrip('/')
        if base.endswith('/v1') or base.endswith('/v2'):
            base = base[:-3]
        return base.rstrip('/')

    def _v2(self) -> bool:
        return self._detect_api_version() == 'v2'

    def _safe_call(self, method, url, **kwargs):
        """带重试的请求封装"""
        headers = {"Authorization": f"Bearer {self.api_key}"}

        for attempt in range(self.max_retries):
            try:
                if method.upper() == 'POST':
                    response = requests.post(url, headers=headers, **kwargs)
                elif method.upper() == 'GET':
                    response = requests.get(url, headers=headers, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()
            except (requests.exceptions.ProxyError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
                maxkb_logger.error(f"⚠️ 网络错误: {e}，正在重试 {attempt + 1}/{self.max_retries}...")
                time.sleep(self.retry_delay)
            except requests.exceptions.HTTPError as e:
                maxkb_logger.error(f"HTTP 错误: {e}")
                raise RuntimeError(f"HTTP 请求失败: {e.response.text if hasattr(e, 'response') else str(e)}")

        raise RuntimeError("多次重试后仍无法连接到 MiniMax API，请检查代理或网络配置")

    def generate_video(self, prompt, negative_prompt=None, first_frame_url=None, last_frame_url=None, **kwargs):
        """
        生成视频
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

    def _build_v2_payload(self, prompt, first_frame_url, last_frame_url):
        content = [{"type": "text", "text": prompt}]
        if first_frame_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": first_frame_url},
                "role": "first_frame",
            })
        if last_frame_url:
            content.append({
                "type": "image_url",
                "image_url": {"url": last_frame_url},
                "role": "last_frame",
            })

        payload = {
            "model": self.model_name,
            "content": content,
        }
        # V2 必需的 resolution / duration，以及可选的 ratio / callback_url 均来自 params
        for key in self.v2_extra_fields:
            if key in self.params:
                payload[key] = self.params[key]
        return payload

    def _generate_video_v2(self, prompt, first_frame_url=None, last_frame_url=None, **kwargs):
        base_url = f"{self._base_url()}/v2/video_generation"
        payload = self._build_v2_payload(prompt, first_frame_url, last_frame_url)

        maxkb_logger.info(f"提交视频生成任务(V2/H3)，模型: {self.model_name}")
        response_data = self._safe_call('POST', base_url, json=payload)

        task_id = response_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"提交任务失败，未获取到 task_id: {response_data}")

        maxkb_logger.info(f"任务已提交，task_id: {task_id}")
        return self._poll_task_status_v2(task_id)

    def _poll_task_status_v2(self, task_id: str) -> str:
        """轮询 V2 任务状态，成功时直接返回视频 URL。"""
        query_url = f"{self._base_url()}/v2/query/video_generation/{task_id}"
        max_attempts = 60  # 最多轮询 60 次（约 10 分钟）

        for attempt in range(max_attempts):
            response_data = self._safe_call('GET', query_url)
            task = response_data.get("task") or response_data
            status = task.get("status")

            maxkb_logger.info(f"当前任务状态 (尝试 {attempt + 1}/{max_attempts}): {status}")

            if status in self.v2_success_status:
                content = task.get("content") or {}
                video_url = content.get("url")
                if not video_url:
                    raise RuntimeError(f"任务成功但未获取到视频 URL: {response_data}")
                maxkb_logger.info(f"任务处理成功，视频 URL: {video_url}")
                return video_url
            elif status in self.v2_fail_status:
                error_msg = self._extract_error(task, response_data)
                raise RuntimeError(f"视频生成失败: {error_msg}")
            else:
                # queued / running 等状态，继续轮询
                time.sleep(self.retry_delay)

        raise RuntimeError(f"任务超时：经过 {max_attempts} 次轮询后仍未完成")

    @staticmethod
    def _extract_error(task: dict, response_data: dict) -> str:
        for container in (task, response_data):
            if not isinstance(container, dict):
                continue
            for key in ("error_message", "error", "detail", "message", "msg"):
                value = container.get(key)
                if value:
                    return str(value)
        return "未知错误"

    # ---------- V1 流程（兼容老接口） ----------

    def _generate_video_v1(self, prompt, first_frame_url=None, last_frame_url=None, **kwargs):
        base_url = f"{self._base_url()}/v1/video_generation"

        # 构建基础参数
        payload = {
            "prompt": prompt,
            "model": self.model_name,
        }

        # 根据提供的参数判断生成模式
        if first_frame_url and last_frame_url:
            payload["first_frame_image"] = first_frame_url
            payload["last_frame_image"] = last_frame_url
            maxkb_logger.info("使用首尾帧模式生成视频")
        elif first_frame_url:
            payload["first_frame_image"] = first_frame_url
            maxkb_logger.info("使用图生视频模式")
        else:
            maxkb_logger.info("使用文生视频模式")

        # 合并额外参数（duration, resolution 等），跳过版本探测专用字段
        payload.update({k: v for k, v in self.params.items() if k != 'api_version'})

        # --- 步骤 1: 提交任务 ---
        maxkb_logger.info(f"提交视频生成任务，模型: {self.model_name}")
        response_data = self._safe_call('POST', base_url, json=payload)

        task_id = response_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"提交任务失败，未获取到 task_id: {response_data}")

        maxkb_logger.info(f"任务已提交，task_id: {task_id}")

        # --- 步骤 2: 轮询查询任务状态 ---
        query_url = f"{self._base_url()}/v1/query/video_generation"
        file_id = self._poll_task_status_v1(query_url, task_id)

        # --- 步骤 3: 获取视频下载链接 ---
        return self._get_video_download_url_v1(file_id)

    def _poll_task_status_v1(self, query_url: str, task_id: str) -> str:
        """轮询 V1 任务状态，直至成功或失败"""
        params = {"task_id": task_id}
        max_attempts = 60  # 最多轮询 60 次（约 10 分钟）

        for attempt in range(max_attempts):
            response_data = self._safe_call('GET', query_url, params=params)
            status = response_data.get("status")

            maxkb_logger.info(f"当前任务状态 (尝试 {attempt + 1}/{max_attempts}): {status}")

            if status in self.v2_success_status:
                file_id = response_data.get("file_id")
                if not file_id:
                    raise RuntimeError(f"任务成功但未获取到 file_id: {response_data}")
                maxkb_logger.info(f"任务处理成功，file_id: {file_id}")
                return file_id
            elif status in self.v2_fail_status:
                error_msg = response_data.get("error_message", "未知错误")
                maxkb_logger.error(f"视频生成失败: {error_msg}")
                raise RuntimeError(f"视频生成失败: {error_msg}")
            else:
                # 任务仍在处理中，等待后继续轮询
                time.sleep(self.retry_delay)

        raise RuntimeError(f"任务超时：经过 {max_attempts} 次轮询后仍未完成")

    def _get_video_download_url_v1(self, file_id: str) -> str:
        """根据 file_id 获取视频下载链接（V1）"""
        retrieve_url = f"{self._base_url()}/v1/files/retrieve"
        params = {"file_id": file_id}

        response_data = self._safe_call('GET', retrieve_url, params=params)

        file_info = response_data.get("file", {})
        download_url = file_info.get("download_url")

        if not download_url:
            raise RuntimeError(f"获取下载链接失败: {response_data}")

        return download_url
