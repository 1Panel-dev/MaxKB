# coding=utf-8
"""
    @project: maxkb
    @file: image_ocr_split_handle.py
    @desc: 图片文件（PNG/JPG/...）入库时自动 OCR，识别文本再走标准 split 流程。
"""
import traceback
from typing import List

from common.handle.base_split_handle import BaseSplitHandle
from common.handle.impl.ocr import OcrConfigError, OcrError, get_ocr_provider
from common.utils.logger import maxkb_logger
from common.utils.split_model import SplitModel
from system_manage.serializers.ocr_setting import OcrSettingSerializer

IMAGE_EXT = ('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff', '.webp', '.heif', '.heic')


class ImageOcrSplitHandle(BaseSplitHandle):
    def support(self, file, get_buffer):
        name = (file.name or '').lower()
        return name.endswith(IMAGE_EXT)

    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        try:
            ocr_config = OcrSettingSerializer.one()
            provider = get_ocr_provider(ocr_config)
        except OcrConfigError as e:
            # 用户未配置 OCR：返回带提示的段落，让用户知道为什么文档"空了"
            maxkb_logger.warning(f"OCR not configured for image upload {file.name}: {e}")
            return {
                'name': file.name,
                'content': [{
                    'title': file.name,
                    'content': f'[图片 OCR 未启用：{e}]'
                }]
            }
        except Exception as e:
            maxkb_logger.error(f"OCR provider init failed for {file.name}: {e}, {traceback.format_exc()}")
            return {'name': file.name, 'content': []}

        try:
            buffer = get_buffer(file)
            text = provider.recognize(buffer)
        except OcrError as e:
            maxkb_logger.error(f"OCR failed for image {file.name}: {e}")
            return {
                'name': file.name,
                'content': [{'title': file.name, 'content': f'[OCR 失败：{e}]'}]
            }
        except Exception as e:
            maxkb_logger.error(f"OCR unexpected error for image {file.name}: {e}, {traceback.format_exc()}")
            return {'name': file.name, 'content': []}

        if not text or not text.strip():
            return {
                'name': file.name,
                'content': [{'title': file.name, 'content': '[图片中未识别出文字]'}]
            }

        # 走与文本文件相同的拆分逻辑，让用户配置的 chunk size / pattern 生效
        try:
            if isinstance(limit, str):
                limit = int(limit)
            split_model = SplitModel(pattern_list, with_filter=with_filter, limit=limit)
            paragraphs = split_model.parse(text)
        except Exception as e:
            maxkb_logger.error(f"OCR text split failed for {file.name}: {e}")
            paragraphs = [{'title': file.name, 'content': text}]

        return {'name': file.name, 'content': paragraphs}

    def get_content(self, file, save_image):
        """工作流 document-extract 等节点会走这条路，简单返回 OCR 文本。"""
        try:
            ocr_config = OcrSettingSerializer.one()
            provider = get_ocr_provider(ocr_config)
            return provider.recognize(file.read()) or ''
        except OcrConfigError as e:
            maxkb_logger.warning(f"OCR not configured (get_content): {e}")
            return f'[OCR 未启用：{e}]'
        except Exception as e:
            maxkb_logger.error(f"OCR get_content error: {e}")
            return ''
