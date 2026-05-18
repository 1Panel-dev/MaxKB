
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.api_base = kwargs.get('api_base', 'https://api.minimaxi.com/v1')
        self.model_name = kwargs.get('model_name')
        self.params = kwargs.get('params', {})
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = 10

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value

        api_base = model_credential.get('api_base','https://api.minimaxi.com/v1')

        return GenerationVideoModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            api_base=api_base,
            **optional_params,
        )

    def check_auth(self):
        return True

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
        base_url = f"{self.api_base}/video_generation"

        # 构建基础参数
        payload = {
            "prompt": prompt,
            "model": self.model_name,
        }

        # 根据提供的参数判断生成模式
        if first_frame_url and last_frame_url:
            # 模式三：首尾帧生成视频
            payload["first_frame_image"] = first_frame_url
            payload["last_frame_image"] = last_frame_url
            maxkb_logger.info("使用首尾帧模式生成视频")
        elif first_frame_url:
            # 模式二：图生视频
            payload["first_frame_image"] = first_frame_url
            maxkb_logger.info("使用图生视频模式")
        else:
            # 模式一：文生视频
            maxkb_logger.info("使用文生视频模式")

        # 合并额外参数（duration, resolution 等）
        payload.update(self.params)

        # --- 步骤 1: 提交任务 ---
        maxkb_logger.info(f"提交视频生成任务，模型: {self.model_name}")
        response_data = self._safe_call('POST', base_url, json=payload)

        task_id = response_data.get("task_id")
        if not task_id:
            raise RuntimeError(f"提交任务失败，未获取到 task_id: {response_data}")

        maxkb_logger.info(f"任务已提交，task_id: {task_id}")

        # --- 步骤 2: 轮询查询任务状态 ---
        query_url = f"{self.api_base}/query/video_generation"
        file_id = self._poll_task_status(query_url, task_id)

        # --- 步骤 3: 获取视频下载链接 ---
        video_url = self._get_video_download_url(file_id)

        maxkb_logger.info(f"视频生成完成！视频 URL: {video_url}")
        return video_url

    def _poll_task_status(self, query_url: str, task_id: str) -> str:
        """轮询任务状态，直至成功或失败"""
        params = {"task_id": task_id}
        max_attempts = 60  # 最多轮询 60 次（约 10 分钟）

        for attempt in range(max_attempts):
            response_data = self._safe_call('GET', query_url, params=params)
            status = response_data.get("status")

            maxkb_logger.info(f"当前任务状态 (尝试 {attempt + 1}/{max_attempts}): {status}")

            if status == "Success":
                file_id = response_data.get("file_id")
                if not file_id:
                    raise RuntimeError(f"任务成功但未获取到 file_id: {response_data}")
                maxkb_logger.info(f"任务处理成功，file_id: {file_id}")
                return file_id
            elif status == "Fail":
                error_msg = response_data.get("error_message", "未知错误")
                maxkb_logger.error(f"视频生成失败: {error_msg}")
                raise RuntimeError(f"视频生成失败: {error_msg}")
            else:
                # 任务仍在处理中，等待后继续轮询
                time.sleep(self.retry_delay)

        raise RuntimeError(f"任务超时：经过 {max_attempts} 次轮询后仍未完成")

    def _get_video_download_url(self, file_id: str) -> str:
        """根据 file_id 获取视频下载链接"""
        retrieve_url = f"{self.api_base}/files/retrieve"
        params = {"file_id": file_id}

        response_data = self._safe_call('GET', retrieve_url, params=params)

        file_info = response_data.get("file", {})
        download_url = file_info.get("download_url")

        if not download_url:
            raise RuntimeError(f"获取下载链接失败: {response_data}")

        return download_url
