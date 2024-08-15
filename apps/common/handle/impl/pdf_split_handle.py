# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： text_split_handle.py
    @date：2024/3/27 18:19
    @desc:
"""
import re
from typing import List

import pypdf
import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
                        re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
                        re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*"),
                        re.compile("(?<!\n)\n\n+")]


def number_to_text(pdf_document, page_number):
    return pdf_document[page_number].page_content


def check_pdf_is_image(pdf_path):
    try:
        # 打开PDF文件
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]

                # 尝试提取文本
                text = page.extract_text()
                if text and text.strip():  # 如果页面中有文本内容
                    return False  # 不是纯图片
                else:
                    return True  # 可能是图片或扫描件

    except Exception as e:
        print(f"Error: {e}")
        return None


class PdfSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件保存到临时文件中
            for chunk in file.chunks():
                temp_file.write(chunk)
            # 获取临时文件的路径
            temp_file_path = temp_file.name

        try:
            if check_pdf_is_image(temp_file_path):
                loader = PyPDFLoader(temp_file_path, extract_images=True)
            else:
                loader = PyPDFLoader(temp_file_path, extract_images=False)
            pdf_document = loader.load()
            content = "\n".join([number_to_text(pdf_document, page_number) for page_number in range(len(pdf_document))])
            if pattern_list is not None and len(pattern_list) > 0:
                split_model = SplitModel(pattern_list, with_filter, limit)
            else:
                split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
        except BaseException as e:
            return {'name': file.name,
                    'content': []}
        finally:
            # 处理完后可以删除临时文件
            os.remove(temp_file_path)

        return {'name': file.name,
                'content': split_model.parse(content)
                }

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".pdf"):
            return True
        return False
