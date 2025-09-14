import time
from http import HTTPStatus
from typing import Dict, Optional
import requests
from dashscope import VideoSynthesis
from langchain_core.messages import HumanMessage
from django.utils.translation import gettext

from langchain_community.chat_models import ChatTongyi
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.base_ttv import BaseGenerationVideo
from common.utils.logger import maxkb_logger


class GenerationVideoModel(MaxKBBaseModel, BaseGenerationVideo):
    api_key: str
    model_name: str
    params: dict
    max_retries: int = 3
    retry_delay: int = 5  # seconds

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get('api_key')
        self.model_name = kwargs.get('model_name')
        self.params = kwargs.get('params', {})
        self.max_retries = kwargs.get('max_retries', 3)
        self.retry_delay = 5

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {'params': {}}
        for key, value in model_kwargs.items():
            if key not in ['model_id', 'use_local', 'streaming']:
                optional_params['params'][key] = value
        return GenerationVideoModel(
            model_name=model_name,
            api_key=model_credential.get('api_key'),
            **optional_params,
        )

    def check_auth(self):
        chat = ChatTongyi(api_key=self.api_key, model_name='qwen-max')
        self._safe_call(chat.invoke, input=[HumanMessage([{"type": "text", "text": gettext('Hello')}])])

    def _safe_call(self, func, **kwargs):
        """带重试的请求封装"""
        for attempt in range(self.max_retries):
            try:
                rsp = func(**kwargs)
                return rsp
            except (requests.exceptions.ProxyError,
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout) as e:
                maxkb_logger.error(f"⚠️ 网络错误: {e}，正在重试 {attempt + 1}/{self.max_retries}...")
                time.sleep(self.retry_delay)
        raise RuntimeError("多次重试后仍无法连接到 DashScope API，请检查代理或网络配置")

    # --- 通用异步生成函数 ---
    def generate_video(self, prompt, negative_prompt=None, first_frame_url=None, last_frame_url=None, **kwargs):
        """
            prompt: 文本描述
            negative_prompt: 反向文本描述
            first_frame_url: 起始关键帧图片 URL (KF2V 必填)
            last_frame_url: 结束关键帧图片 URL (KF2V 必填)
            如果没有提供last_frame_url，则表示只提供了first_frame_url，生成的是单关键帧视频（KFV） 参数是img_url
            """

        # 构建基础参数
        params = {"api_key": self.api_key, "prompt": prompt, "model": self.model_name,
                  "negative_prompt": negative_prompt}
        if first_frame_url and last_frame_url:
            params['first_frame_url'] = first_frame_url
            params["last_frame_url"] = last_frame_url
        elif first_frame_url:
            params['img_url'] = first_frame_url

        # 合并所有额外参数
        params.update(self.params)

        # --- 异步提交任务 ---
        rsp = self._safe_call(VideoSynthesis.async_call, **params)
        if rsp.status_code != HTTPStatus.OK:
            maxkb_logger.info('提交任务失败，status_code: %s, code: %s, message: %s' %
                              (rsp.status_code, rsp.code, rsp.message))
            return None

        maxkb_logger.info("task_id:", rsp.output.task_id)

        # --- 查询任务状态 ---
        status = self._safe_call(VideoSynthesis.fetch, task=rsp, api_key=self.api_key)
        if status.status_code == HTTPStatus.OK:
            maxkb_logger.info("当前任务状态:", status.output.task_status)
        else:
            maxkb_logger.error('获取任务状态失败，status_code: %s, code: %s, message: %s' %
                               (status.status_code, status.code, status.message))

        # --- 等待任务完成 ---
        rsp = self._safe_call(VideoSynthesis.wait, task=rsp, api_key=self.api_key)
        if rsp.status_code == HTTPStatus.OK:
            maxkb_logger.info("视频生成完成！视频 URL:", rsp.output.video_url)
            return rsp.output.video_url
        else:
            maxkb_logger.error('生成失败，status_code: %s, code: %s, message: %s' %
                               (rsp.status_code, rsp.code, rsp.message))
            return None
