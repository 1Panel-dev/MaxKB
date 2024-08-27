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

import fitz
import os
import tempfile
import logging
from langchain_community.document_loaders import PyPDFLoader

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel

import time

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
                        re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
                        re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*"),
                        re.compile("(?<!\n)\n\n+")]

max_kb = logging.getLogger("max_kb")


class PdfSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件保存到临时文件中
            for chunk in file.chunks():
                temp_file.write(chunk)
            # 获取临时文件的路径
            temp_file_path = temp_file.name

        pdf_document = fitz.open(temp_file_path)
        try:
            content = ""
            for page_num in range(len(pdf_document)):
                start_time = time.time()
                page = pdf_document.load_page(page_num)
                text = page.get_text()

                if text and text.strip():  # 如果页面中有文本内容
                    page_content = text
                else:
                    try:
                        new_doc = fitz.open()
                        new_doc.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
                        page_num_pdf = tempfile.gettempdir() + f"/{file.name}_{page_num}.pdf"
                        new_doc.save(page_num_pdf)
                        new_doc.close()

                        loader = PyPDFLoader(page_num_pdf, extract_images=True)
                        page_content = "\n" + loader.load()[0].page_content
                    except NotImplementedError as e:
                        # 文件格式不支持，直接退出
                        raise e
                    except BaseException as e:
                        # 当页出错继续进行下一页，防止一个页面出错导致整个文件解析失败
                        max_kb.error(f"File: {file.name}, Page: {page_num + 1}, error: {e}")
                        continue
                    finally:
                        os.remove(page_num_pdf)

                content += page_content

                elapsed_time = time.time() - start_time
                # todo 实现进度条代替下面的普通输出
                max_kb.debug(
                    f"File: {file.name}, Page: {page_num + 1}, Time : {elapsed_time: .3f}s,   content-length: {len(page_content)}")
            if pattern_list is not None and len(pattern_list) > 0:
                split_model = SplitModel(pattern_list, with_filter, limit)
            else:
                split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)


        except BaseException as e:
            max_kb.error(f"File: {file.name}, error: {e}")
            return {'name': file.name,
                    'content': []}
        finally:
            pdf_document.close()
            # 处理完后可以删除临时文件
            os.remove(temp_file_path)

        return {'name': file.name,
                'content': split_model.parse(content)
                }

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".pdf") or file_name.endswith(".PDF"):
            return True
        return False
