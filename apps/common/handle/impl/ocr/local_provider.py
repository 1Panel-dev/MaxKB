# coding=utf-8
"""
    @project: maxkb
    @file: local_provider.py
    @desc: 本地 OCR provider，基于 rapidocr-onnxruntime。

    依赖采用 **lazy import** 策略：
      - rapidocr-onnxruntime 不强制写进 pyproject.toml（CPU-only 也要 ~150 MB）
      - 用户在系统设置选择"本地 OCR"模式时，必须先在容器内执行：
            pip install rapidocr-onnxruntime
      - 未安装时 LocalOcrProvider 在初始化阶段就抛 OcrConfigError，
        让前端在测试 OCR 配置时直接收到清晰提示。
"""
import io

from common.handle.impl.ocr.provider import OcrProvider, OcrError, OcrConfigError
from common.utils.logger import maxkb_logger

_INSTALL_HINT = (
    "本地 OCR 依赖未安装。请在 MaxKB 运行环境中执行："
    "pip install rapidocr-onnxruntime onnxruntime"
)


class LocalOcrProvider(OcrProvider):
    def __init__(self, language: str = 'ch'):
        self.language = language
        try:
            from rapidocr_onnxruntime import RapidOCR  # type: ignore
        except ImportError as e:
            raise OcrConfigError(_INSTALL_HINT) from e
        # 单例化 engine，避免每次 OCR 重新加载模型
        self._engine = RapidOCR()

    def recognize(self, image_bytes: bytes) -> str:
        if not image_bytes:
            return ''
        try:
            # RapidOCR 接受 bytes / PIL.Image / np.ndarray / 文件路径
            # 这里直接用 BytesIO 给它（rapidocr_onnxruntime 支持 file-like 或 bytes）
            result, _elapse = self._engine(io.BytesIO(image_bytes).getvalue())
        except Exception as e:
            maxkb_logger.error(f"OCR (local): recognize failed: {e}")
            raise OcrError(f"本地 OCR 识别失败：{e}")

        if not result:
            return ''
        # result 是 [[bbox, text, score], ...]，按从上到下、从左到右的顺序拼接
        lines = []
        for item in result:
            if not item or len(item) < 2:
                continue
            text = item[1]
            if text:
                lines.append(str(text))
        return '\n'.join(lines).strip()
