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
import traceback
from typing import List

import fitz
from langchain_community.document_loaders import PyPDFLoader

from common.handle.base_split_handle import BaseSplitHandle
from common.util.split_model import SplitModel
from django.utils.translation import gettext_lazy as _

default_pattern_list = [re.compile('(?<=^)# .*|(?<=\\n)# .*'),
                        re.compile('(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*'),
                        re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
                        re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*"),
                        re.compile("(?<!\n)\n\n+")]

max_kb = logging.getLogger("max_kb")


def check_links_in_pdf(doc):
    for page_number in range(len(doc)):
        page = doc[page_number]
        links = page.get_links()
        if links:
            for link in links:
                if link['kind'] == 1:
                    return True
    return False

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
            result = self.handle_toc(pdf_document, limit)
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

            # Null characters are not allowed.
            content = content.replace('\0', '')

            elapsed_time = time.time() - start_time
            max_kb.debug(
                f"File: {file.name}, Page: {page_num + 1}, Time : {elapsed_time: .3f}s,   content-length: {len(page_content)}")

        return content

    @staticmethod
    def extract_page_lines(page):
        lines = []
        current_text = []
        current_sizes = []

        def flush_line():
            text = "".join(current_text).strip()
            if text:
                font_size = current_sizes[0] if current_sizes else 0
                lines.append((text, font_size))
            current_text.clear()
            current_sizes.clear()

        def visitor_text(text, cm, tm, font_dict, font_size):
            if text is None:
                return
            parts = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
            for index, part in enumerate(parts):
                current_text.append(part)
                if part.strip() and font_size:
                    current_sizes.append(float(font_size))
                if index < len(parts) - 1:
                    flush_line()

        try:
            page.extract_text(visitor_text=visitor_text)
        except BaseException:
            text = PdfSplitHandle.extract_page_text(page)
            return [(line.strip(), 0) for line in text.splitlines() if line.strip()]
        flush_line()
        if lines:
            return lines

        text = page.extract_text() or ""
        return [(line.strip(), 0) for line in text.splitlines() if line.strip()]

    @staticmethod
    def get_page_image_count(page):
        try:
            return len(page.images)
        except BaseException:
            return 0

    @staticmethod
    def extract_page_text(page):
        return (page.extract_text() or "").replace("\0", "")

    @staticmethod
    def get_toc(doc):
        try:
            outline = doc.outline
        except BaseException:
            return []

        toc = []
        PdfSplitHandle.collect_toc(doc, outline, 1, toc)
        return toc

    @staticmethod
    def collect_toc(doc, outline, level, toc):
        for item in outline:
            if isinstance(item, list):
                PdfSplitHandle.collect_toc(doc, item, level + 1, toc)
                continue

            page_number = PdfSplitHandle.get_destination_page_number(doc, item)
            if page_number is None:
                continue

            title = getattr(item, "title", None)
            if title is None and hasattr(item, "get"):
                title = item.get("/Title")
            if title is None:
                title = str(item)
            toc.append(
                (
                    level,
                    str(title).replace("\0", ""),
                    page_number,
                    PdfSplitHandle.get_destination_top(item),
                )
            )

    @staticmethod
    def get_destination_top(destination):
        top = getattr(destination, "top", None)
        try:
            return float(top)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def extract_page_text_by_position(page, top=None, bottom=None):
        if top is None and bottom is None:
            return PdfSplitHandle.extract_page_text(page)

        text_parts = []

        def visitor_text(text, cm, tm, font_dict, font_size):
            if not text:
                return

            # Text matrix coordinates can be relative to a page-level transform.
            # Convert the text origin to PDF user-space coordinates before comparing
            # it with the outline destination's /Top value.
            x = tm[4] if len(tm) > 4 else 0
            y = tm[5] if len(tm) > 5 else 0
            if len(cm) > 5:
                y = x * cm[1] + y * cm[3] + cm[5]

            if top is not None and y > top:
                return
            if bottom is not None and y <= bottom:
                return
            text_parts.append(text)

        try:
            page.extract_text(visitor_text=visitor_text)
        except BaseException:
            return PdfSplitHandle.extract_page_text(page)
        return "".join(text_parts).replace("\0", "")

    @staticmethod
    def remove_leading_title(text, *titles):
        for title in titles:
            title = title.strip()
            if not title:
                continue
            pattern = r"^\s*" + r"\s*".join(re.escape(char) for char in title)
            stripped_text, count = re.subn(pattern, "", text, count=1)
            if count:
                return stripped_text
        return text

    @staticmethod
    def handle_toc(doc, limit):
        # 找到目录
        toc = PdfSplitHandle.get_toc(doc)
        if toc is None or len(toc) == 0:
            return None

        # 创建存储章节内容的数组
        chapters = []

        # 遍历目录并按章节提取文本
        for i, entry in enumerate(toc):
            level, title, start_page, start_top = entry
            chapter_title = title
            # 确定结束页码，如果是最后一个章节则到文档末尾
            if i + 1 < len(toc):
                _next_level, next_title, next_start_page, next_top = toc[i + 1]
                # A positioned bookmark can start partway down a page. Include that
                # page and keep only the text above the next bookmark for this chapter.
                end_page = next_start_page if next_top is not None else next_start_page - 1
            else:
                end_page = len(doc.pages) - 1
                next_title = None
                next_start_page = None
                next_top = None
            end_page = max(start_page, end_page)

            # 去掉标题中的符号
            title = PdfSplitHandle.handle_chapter_title(title)

            # 提取该章节的文本内容
            chapter_text = ""
            for page_num in range(start_page, end_page + 1):
                page_top = start_top if page_num == start_page else None
                page_bottom = next_top if page_num == next_start_page else None
                text = PdfSplitHandle.extract_page_text_by_position(doc.pages[page_num], page_top, page_bottom)
                text = re.sub(r"(?<!。)\n+", "", text)
                text = re.sub(r"(?<!.)\n+", "", text)

                if page_num == start_page:
                    if start_top is not None:
                        text = PdfSplitHandle.remove_leading_title(text, chapter_title, title)
                    else:
                        idx = text.find(title)
                        if idx > -1:
                            text = text[idx + len(title):]

                if next_title is not None and next_top is None:
                    handled_next_title = PdfSplitHandle.handle_chapter_title(next_title)
                    idx = text.find(handled_next_title)
                    if idx > -1:
                        text = text[:idx]

                chapter_text += text  # 提取文本

            # Null characters are not allowed.
            chapter_text = chapter_text.replace("\0", "")
            # 限制标题长度
            real_chapter_title = chapter_title[:256]
            # 限制章节内容长度
            if 0 < limit < len(chapter_text):
                split_text = PdfSplitHandle.split_text(chapter_text, limit)
                for text in split_text:
                    chapters.append(
                        {"title": real_chapter_title, "content": text.encode("utf-8", "ignore").decode("utf-8")}
                    )
            else:
                chapters.append(
                    {
                        "title": real_chapter_title,
                        "content": (chapter_text if chapter_text else real_chapter_title)
                        .encode("utf-8", "ignore")
                        .decode("utf-8"),
                    }
                )
            # 保存章节内容和章节标题
        return chapters

    @staticmethod
    def handle_links(doc, pattern_list, with_filter, limit):
        # 检查文档是否包含内部链接
        if not check_links_in_pdf(doc):
            return
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

                    # Null characters are not allowed.
                    chapter_text = chapter_text.replace('\0', '')

                    # 限制章节内容长度
                    if 0 < limit < len(chapter_text):
                        split_text = PdfSplitHandle.split_text(chapter_text, limit)
                        for text in split_text:
                            chapters.append({"title": link_title, "content": text})
                    else:
                        # 保存章节信息
                        chapters.append({"title": link_title, "content": chapter_text})

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
                max_kb.error(_('This document has no preface and is treated as ordinary text: {e}').format(e=e))
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

    @staticmethod
    def split_text(text, length):
        segments = []
        current_segment = ""

        for char in text:
            current_segment += char
            if len(current_segment) >= length:
                # 查找最近的句号
                last_period_index = current_segment.rfind('.')
                if last_period_index != -1:
                    segments.append(current_segment[:last_period_index + 1])
                    current_segment = current_segment[last_period_index + 1:]  # 更新当前段落
                else:
                    segments.append(current_segment)
                    current_segment = ""

        # 处理剩余的部分
        if current_segment:
            segments.append(current_segment)

        return segments

    @staticmethod
    def handle_chapter_title(title):
        title = re.sub(r'[一二三四五六七八九十\s*]、\s*', '', title)
        title = re.sub(r'第[一二三四五六七八九十]章\s*', '', title)
        return title

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".pdf") or file_name.endswith(".PDF"):
            return True
        return False

    def get_content(self, file, save_image):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件保存到临时文件中
            temp_file.write(file.read())
            # 获取临时文件的路径
            temp_file_path = temp_file.name

        pdf_document = fitz.open(temp_file_path)
        try:
            return self.handle_pdf_content(file, pdf_document)
        except BaseException as e:
            traceback.print_exception(e)
            return f'{e}'