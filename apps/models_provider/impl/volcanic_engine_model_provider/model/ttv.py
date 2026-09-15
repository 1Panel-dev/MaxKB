import time
from typing import Dict
from models_provider.base_model_provider import MaxKBBaseModel
from models_provider.base_ttv import BaseGenerationVideo
from common.utils.logger import maxkb_logger
from volcenginesdkarkruntime import Ark

# 视频生成接口支持的直接传参字段
# 文档: https://www.volcengine.com/docs/82379/1520758
VIDEO_PARAM_KEYS = (
    "resolution",
    "ratio",
    "duration",
    "frames",
    "watermark",
    "camera_fixed",
    "seed",
    "generate_audio",
    "draft",
    "return_last_frame",
    "service_tier",
    "callback_url",
    "execution_expires_after",
    "priority",
    "safety_identifier",
)

INT_PARAM_KEYS = ("duration", "frames", "seed", "execution_expires_after", "priority")


class GenerationVideoModel(MaxKBBaseModel, BaseGenerationVideo):
    api_key: str
    base_url: str
    model_name: str
    params: dict
    max_retries: int = 3
    retry_delay: int = 5  # seconds

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_key = kwargs.get("api_key")
        self.base_url = kwargs.get("base_url")
        self.model_name = kwargs.get("model_name")
        self.params = kwargs.get("params", {})
        self.retry_delay = 5

    @staticmethod
    def is_cache_model():
        return False

    @staticmethod
    def new_instance(model_type, model_name, model_credential: Dict[str, object], **model_kwargs):
        optional_params = {"params": {}}
        for key, value in model_kwargs.items():
            if key not in ["model_id", "use_local", "streaming"]:
                optional_params["params"][key] = value
        return GenerationVideoModel(
            model_name=model_name,
            api_key=model_credential.get("api_key"),
            base_url=model_credential.get("base_url", "https://ark.cn-beijing.volces.com/api/v3"),
            **optional_params,
        )

    def check_auth(self):
        return True

    def _build_params(self) -> dict:
        """把参数转换为视频生成接口的顶层字段，接口不支持的字段放入 extra_body"""
        params = {}
        extra_body = {}
        for key, value in (self.params or {}).items():
            if value is None or value == "":
                continue
            name = str(key).replace(" ", "_").lower()
            if name == "camerafixed":
                name = "camera_fixed"
            if name in VIDEO_PARAM_KEYS:
                params[name] = int(value) if name in INT_PARAM_KEYS else value
            else:
                extra_body[name] = value
        if extra_body:
            params["extra_body"] = extra_body
        return params

    def _poll_task(self, client: Ark, task_id: str, interval: int = 30):
        """轮询任务状态，直到完成"""
        while True:
            result = client.content_generation.tasks.get(task_id=task_id)
            status = getattr(result, "status", None)
            maxkb_logger.info(f"[ArkVideo] Task {task_id} status={status}")

            if status in ("succeeded", "failed", "cancelled"):
                return result

            time.sleep(interval)

    # --- 通用异步生成函数 ---
    def generate_video(self, prompt, negative_prompt=None, first_frame_url=None, last_frame_url=None, **kwargs):
        client = Ark(api_key=self.api_key, base_url=self.base_url)
        content = [{"type": "text", "text": prompt}]

        if first_frame_url:
            content.append({"type": "image_url", "image_url": {"url": first_frame_url}, "role": "first_frame"})
        if last_frame_url:
            content.append({"type": "image_url", "image_url": {"url": last_frame_url}, "role": "last_frame"})

        task = client.content_generation.tasks.create(model=self.model_name, content=content, **self._build_params())
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
            raise e
        maxkb_logger.info(f"[ArkVideo] 视频地址 {result.content.video_url}")
        return result.content.video_url
