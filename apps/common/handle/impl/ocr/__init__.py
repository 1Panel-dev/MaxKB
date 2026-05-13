# coding=utf-8
"""
    @project: maxkb
    @file: __init__.py
    @desc: OCR provider 包入口。
"""
from .provider import OcrProvider, get_ocr_provider, OcrConfigError, OcrError

__all__ = ['OcrProvider', 'get_ocr_provider', 'OcrConfigError', 'OcrError']
