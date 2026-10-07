# coding=utf-8
"""
@project: maxkb
@file: pdf_ocr.py
@desc: Opt-in local text OCR for image-only PDF pages.
"""
import io
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener

from common.exception.app_exception import AppApiException
from maxkb.const import CONFIG, PROJECT_DIR

# Local PDFs must never follow a machine-wide HTTP proxy configuration.
urlopen = build_opener(ProxyHandler({})).open


class PdfOcrError(AppApiException):
    def __init__(self, message):
        super().__init__(500, message)


def ocr_enabled():
    return str(CONFIG.get("OCR_ENABLED", False)).lower() in ("1", "true", "yes")


def recognize_pdf_page(pdf_document, page_number):
    """Only send the requested page to the local OCR process, not the entire source file."""
    from pypdf import PdfWriter

    base = str(CONFIG.get("OCR_URL", "http://127.0.0.1:11637")).rstrip("/")
    parsed = urlparse(base)
    if parsed.scheme != "http" or parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        raise PdfOcrError("OCR_URL 必须指向本机 OCR 服务")
    token = str(CONFIG.get("OCR_TOKEN", ""))
    if not token:
        token_file = Path(CONFIG.get("OCR_TOKEN_FILE", Path(PROJECT_DIR) / "installer/ocr/runtime/token"))
        try:
            token = token_file.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise PdfOcrError("本机 OCR 服务尚未启动，请运行 installer/ocr/start.ps1") from exc
    writer = PdfWriter()
    writer.add_page(pdf_document.pages[page_number - 1])
    buffer = io.BytesIO()
    writer.write(buffer)
    request = Request(
        base + "/recognize?page=1&dpi=200", data=buffer.getvalue(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/pdf"},
    )
    try:
        # Allow queueing (300 s), model recovery (300 s), inference (300 s) and upload.
        with urlopen(request, timeout=930) as response:
            result = json.load(response)
    except HTTPError as exc:
        exc.close()
        if exc.code == 429:
            message = "OCR 服务正在处理其他请求，排队超时，请稍后重试"
        elif exc.code == 504:
            message = "OCR 识别超时，请检查扫描清晰度及 OCR 服务日志"
        elif exc.code == 401:
            message = "OCR 服务认证失败，请检查本机 token 配置"
        else:
            message = f"OCR 失败（服务状态 {exc.code}），请检查 OCR 服务日志"
        raise PdfOcrError(f"第 {page_number} 页 {message}") from exc
    except (URLError, TimeoutError, ConnectionError, OSError) as exc:
        raise PdfOcrError(f"第 {page_number} 页 OCR 服务不可用或超时，请检查本机 OCR 服务") from exc
    except (ValueError, TypeError) as exc:
        raise PdfOcrError(f"第 {page_number} 页 OCR 返回了无效结果") from exc
    if not isinstance(result, dict):
        raise PdfOcrError(f"第 {page_number} 页 OCR 返回了无效结果")
    text = result.get("text")
    if not isinstance(text, str) or not text.strip():
        raise PdfOcrError(f"第 {page_number} 页未识别到文字，请检查扫描清晰度或移除空白扫描页")
    return text.strip()
