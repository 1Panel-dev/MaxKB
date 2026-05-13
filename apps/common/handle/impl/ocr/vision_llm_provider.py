# coding=utf-8
"""
    @project: maxkb
    @file: vision_llm_provider.py
    @desc: 视觉大模型 OCR provider。复用 models_provider 已接入的多模态模型
           （OpenAI gpt-4o, Anthropic, Gemini, 通义千问 vl, 智谱 glm-4v 等）。
"""
import base64
from imghdr import what

from langchain_core.messages import HumanMessage

from common.handle.impl.ocr.provider import OcrProvider, OcrError, DEFAULT_OCR_PROMPT
from common.utils.logger import maxkb_logger


class VisionLlmOcrProvider(OcrProvider):
    def __init__(self, model_id: str, workspace_id: str = 'default', prompt: str = DEFAULT_OCR_PROMPT):
        self.model_id = model_id
        self.workspace_id = workspace_id
        self.prompt = prompt

    def recognize(self, image_bytes: bytes) -> str:
        if not image_bytes:
            return ''
        # 检测格式（PNG/JPEG/...），imghdr 返回 'png'/'jpeg' 等小写名
        img_format = what(None, image_bytes) or 'png'
        b64 = base64.b64encode(image_bytes).decode('utf-8')
        data_url = f'data:image/{img_format};base64,{b64}'

        try:
            # 延迟 import 避免在 Django 启动早期触发 model provider 链路
            from models_provider.tools import get_model_instance_by_model_workspace_id
            model = get_model_instance_by_model_workspace_id(self.model_id, self.workspace_id)
        except Exception as e:
            maxkb_logger.error(f"OCR: failed to load vision model {self.model_id}: {e}")
            raise OcrError(f"加载视觉模型失败：{e}")

        message = HumanMessage(content=[
            {'type': 'text', 'text': self.prompt},
            {'type': 'image_url', 'image_url': {'url': data_url}},
        ])
        try:
            response = model.invoke([message])
        except Exception as e:
            maxkb_logger.error(f"OCR: vision model invoke failed: {e}")
            raise OcrError(f"视觉模型识别失败：{e}")

        # langchain AIMessage.content 可能是 str 或 list[dict]
        content = response.content if hasattr(response, 'content') else str(response)
        if isinstance(content, list):
            parts = []
            for chunk in content:
                if isinstance(chunk, dict):
                    parts.append(chunk.get('text', ''))
                else:
                    parts.append(str(chunk))
            content = '\n'.join(parts)
        return (content or '').strip()
