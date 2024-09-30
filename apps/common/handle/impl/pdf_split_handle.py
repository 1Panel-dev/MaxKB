# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： text_split_handle.py
    @date：2024/3/27 18:19
    @desc:
"""
import logging
import os
import re
import tempfile
import time
from typing import List

import fitz
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
            # 处理有目录的pdf
            result = self.handle_toc(pdf_document)
            if result is not None:
                return {'name': file.name, 'content': result}

            # 没目录但是有链接的pdf
            result = self.handle_links(pdf_document, pattern_list, with_filter, limit)
            if result is not None and len(result) > 0:
                return {'name': file.name, 'content': result}

            # 没有目录的pdf
            content = self.handle_pdf_content(file, pdf_document)

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

    @staticmethod
    def handle_pdf_content(file, pdf_document):
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
            max_kb.debug(
                f"File: {file.name}, Page: {page_num + 1}, Time : {elapsed_time: .3f}s,   content-length: {len(page_content)}")

        return content

    @staticmethod
    def handle_toc(doc):
        # 找到目录
        toc = doc.get_toc()
        if toc is None or len(toc) == 0:
            return None

        # 创建存储章节内容的数组
        chapters = []

        # 遍历目录并按章节提取文本
        for i, entry in enumerate(toc):
            level, title, start_page = entry
            start_page -= 1  # PyMuPDF 页码从 0 开始，书签页码从 1 开始
            chapter_title = title
            # 确定结束页码，如果是最后一个章节则到文档末尾
            if i + 1 < len(toc):
                end_page = toc[i + 1][2] - 1
            else:
                end_page = doc.page_count - 1

            # 去掉标题中的符号
            title = PdfSplitHandle.handle_chapter_title(title)

            # 提取该章节的文本内容
            chapter_text = ""
            for page_num in range(start_page, end_page + 1):
                page = doc.load_page(page_num)  # 加载页面
                text = page.get_text("text")
                text = re.sub(r'(?<!。)\n+', '', text)
                text = re.sub(r'(?<!.)\n+', '', text)
                # print(f'title: {title}')

                idx = text.find(title)
                if idx > -1:
                    text = text[idx + len(title):]

                if i + 1 < len(toc):
                    l, next_title, next_start_page = toc[i + 1]
                    next_title = PdfSplitHandle.handle_chapter_title(next_title)
                    # print(f'next_title: {next_title}')
                    idx = text.find(next_title)
                    if idx > -1:
                        text = text[:idx]

                chapter_text += text  # 提取文本

            # 保存章节内容和章节标题
            chapters.append({"title": chapter_title, "content": chapter_text})
        return chapters

    @staticmethod
    def handle_chapter_title(title):
        title = re.sub(r'[一二三四五六七八九十\s*]、\s*', '', title)
        title = re.sub(r'第[一二三四五六七八九十]章\s*', '', title)
        return title

    @staticmethod
    def handle_links(doc, pattern_list, with_filter, limit):
        # 创建存储章节内容的数组
        chapters = []
        toc_start_page = -1
        page_content = ""
        handle_pre_toc = True
        # 遍历 PDF 的每一页，查找带有目录链接的页
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            links = page.get_links()
            # 如果目录开始页码未设置，则设置为当前页码
            if len(links) > 0:
                toc_start_page = page_num
            if toc_start_page < 0:
                page_content += page.get_text('text')
            # 检查该页是否包含内部链接（即指向文档内部的页面）
            for num in range(len(links)):
                link = links[num]
                if link['kind'] == 1:  # 'kind' 为 1 表示内部链接
                    # 获取链接目标的页面
                    dest_page = link['page']
                    rect = link['from']  # 获取链接的矩形区域
                    # 如果目录开始页码包括前言部分，则不处理前言部分
                    if dest_page < toc_start_page:
                        handle_pre_toc = False

                    # 提取链接区域的文本作为标题
                    link_title = page.get_text("text", clip=rect).strip().split("\n")[0].replace('.', '').strip()
                    # print(f'link_title: {link_title}')
                    # 提取目标页面内容作为章节开始
                    start_page = dest_page
                    end_page = dest_page
                    # 下一个link
                    next_link = links[num + 1] if num + 1 < len(links) else None
                    next_link_title = None
                    if next_link is not None and next_link['kind'] == 1:
                        rect = next_link['from']
                        next_link_title = page.get_text("text", clip=rect).strip() \
                            .split("\n")[0].replace('.', '').strip()
                        # print(f'next_link_title: {next_link_title}')
                        end_page = next_link['page']

                    # 提取章节内容
                    chapter_text = ""
                    for p_num in range(start_page, end_page + 1):
                        p = doc.load_page(p_num)
                        text = p.get_text("text")
                        text = re.sub(r'(?<!。)\n+', '', text)
                        text = re.sub(r'(?<!.)\n+', '', text)
                        # print(f'\n{text}\n')

                        idx = text.find(link_title)
                        if idx > -1:
                            text = text[idx + len(link_title):]

                        if next_link_title is not None:
                            idx = text.find(next_link_title)
                            if idx > -1:
                                text = text[:idx]
                        chapter_text += text

                    # 保存章节信息
                    chapters.append({
                        "title": link_title,
                        "content": chapter_text
                    })

        # 目录中没有前言部分，手动处理
        if handle_pre_toc:
            pre_toc = []
            lines = page_content.strip().split('\n')
            try:
                for line in lines:
                    if re.match(r'^前\s*言', line):
                        pre_toc.append({'title': line, 'content': ''})
                    else:
                        pre_toc[-1]['content'] += line
                for i in range(len(pre_toc)):
                    pre_toc[i]['content'] = re.sub(r'(?<!。)\n+', '', pre_toc[i]['content'])
                    pre_toc[i]['content'] = re.sub(r'(?<!.)\n+', '', pre_toc[i]['content'])
            except BaseException as e:
                max_kb.info(f'此文档没有前言部分，按照普通文本处理: {e}')
                if pattern_list is not None and len(pattern_list) > 0:
                    split_model = SplitModel(pattern_list, with_filter, limit)
                else:
                    split_model = SplitModel(default_pattern_list, with_filter=with_filter, limit=limit)
                # 插入目录前的部分
                page_content = re.sub(r'(?<!。)\n+', '', page_content)
                page_content = re.sub(r'(?<!.)\n+', '', page_content)
                page_content = page_content.strip()
                pre_toc = split_model.parse(page_content)
            chapters = pre_toc + chapters
        return chapters

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".pdf") or file_name.endswith(".PDF"):
            return True
        return False
