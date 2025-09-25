import base64
import time
from typing import Dict, Optional
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.base_ttv import BaseGenerationVideo
from common.utils.logger import maxkb_logger
from volcenginesdkarkruntime import Ark


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
        return True

    def _build_prompt(self, prompt: str) -> str:
        """拼接参数到 prompt 文本"""
        param_map = {
            "ratio": "rt",
            "duration": "dur",
            "framespersecond": "fps",
            "resolution": "rs",
            "watermark": "wm",
            "camerafixed": "cf",
        }
        for key, value in self.params.items():
            if key in param_map:
                prompt += f" --{param_map[key]} {value}"
        return prompt

    def _poll_task(self, client: Ark, task_id: str, max_wait: int = 60, interval: int = 5):
        """轮询任务状态，直到完成或超时"""
        elapsed = 0
        while elapsed < max_wait:
            result = client.content_generation.tasks.get(task_id=task_id)
            status = getattr(result, "status", None)
            maxkb_logger.info(f"[ArkVideo] Task {task_id} status={status}")

            if status in ("succeeded", "failed", "cancelled"):
                return result

            time.sleep(interval)
            elapsed += interval
        maxkb_logger.warning(f"[ArkVideo] Task {task_id} wait timeout")
        return None

    # --- 通用异步生成函数 ---
    def generate_video(self, prompt, negative_prompt=None, first_frame_url=None, last_frame_url=None, **kwargs):
        client = Ark(api_key=self.api_key)
        # 根据params设置其他参数 豆包的参数和别的不一样  需要拼接在text里
        # --rt 16:9 --dur 5 --fps 24 --rs 720p --wm true --cf false
        prompt = self._build_prompt(prompt)
        content = [{"type": "text", "text": prompt}]

        if first_frame_url:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": first_frame_url
                },
                "role": "first_frame"
            })
        if last_frame_url:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": last_frame_url
                },
                "role": "last_frame"
            })
        create_result = client.content_generation.tasks.create(
            model=self.model_name,
            content=content
        )

        task = client.content_generation.tasks.create(model=self.model_name, content=content)
        task_id = task.id
        maxkb_logger.info(f"[ArkVideo] Created task {task_id}")

        # 轮询获取结果
        result = self._poll_task(client, task_id)
        if not result:
            return {"status": "timeout", "task_id": task_id}

        try:
            if getattr(result, "status", None) in ("succeeded", "failed", "cancelled"):
                client.content_generation.tasks.delete(task_id=task_id)
                maxkb_logger.info(f"[ArkVideo] Deleted task {task_id}")
        except Exception as e:
            maxkb_logger.error(f"[ArkVideo] Failed to delete task {task_id}: {e}")
        maxkb_logger.info("视频地址", result.content.video_url)
        return result.content.video_url
