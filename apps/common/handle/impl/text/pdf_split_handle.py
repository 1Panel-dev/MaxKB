# coding=utf-8
"""
@project: maxkb
@Author：虎
@file： text_split_handle.py
@date：2024/3/27 18:19
@desc:
"""

import os
import re
import tempfile
import time
import traceback
from typing import List

from pypdf import PdfReader
from pypdf.generic import Destination
from django.utils.translation import gettext_lazy as _

from common.handle.base_split_handle import BaseSplitHandle
from common.utils.logger import maxkb_logger
from common.utils.split_model import SplitModel, smart_split_paragraph

default_pattern_list = [
    re.compile("(?<=^)# .*|(?<=\\n)# .*"),
    re.compile("(?<=\\n)(?<!#)## (?!#).*|(?<=^)(?<!#)## (?!#).*"),
    re.compile("(?<=\\n)(?<!#)### (?!#).*|(?<=^)(?<!#)### (?!#).*"),
    re.compile("(?<=\\n)(?<!#)#### (?!#).*|(?<=^)(?<!#)#### (?!#).*"),
    re.compile("(?<=\\n)(?<!#)##### (?!#).*|(?<=^)(?<!#)##### (?!#).*"),
    re.compile("(?<=\\n)(?<!#)###### (?!#).*|(?<=^)(?<!#)###### (?!#).*"),
    re.compile("(?<!\n)\n\n+"),
]


def check_links_in_pdf(doc):
    for page in doc.pages:
        if PdfSplitHandle.get_internal_links(doc, page):
            return True
    return False


def get_pdf_object(value):
    if hasattr(value, "get_object"):
        return value.get_object()
    return value


class PdfSplitHandle(BaseSplitHandle):
    def handle(
        self,
        file,
        pattern_list: List,
        with_filter: bool,
        limit: int,
        get_buffer,
        save_image,
    ):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # 将上传的文件保存到临时文件中
            for chunk in file.chunks():
                temp_file.write(chunk)
            # 获取临时文件的路径
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, "rb") as pdf_file:
                pdf_document = PdfReader(pdf_file)
                if type(limit) is str:
                    limit = int(limit)
                if type(with_filter) is str:
                    with_filter = with_filter.lower() == "true"
                # 处理有目录的pdf
                result = self.handle_toc(pdf_document, limit)
                if result is not None:
                    return {"name": file.name, "content": result}

                # 没目录但是有链接的pdf
                result = self.handle_links(
                    pdf_document, pattern_list, with_filter, limit
                )
                if result is not None and len(result) > 0:
                    return {"name": file.name, "content": result}

                # 没有目录的pdf
                content = self.handle_pdf_content(file, pdf_document)

                if pattern_list is not None and len(pattern_list) > 0:
                    split_model = SplitModel(pattern_list, with_filter, limit)
                else:
                    split_model = SplitModel(
                        default_pattern_list, with_filter=with_filter, limit=limit
                    )
        except BaseException as e:
            maxkb_logger.error(
                f"File: {file.name}, error: {e}, {traceback.format_exc()}"
            )
            return {"name": file.name, "content": []}
        finally:
            # 处理完后可以删除临时文件
            os.remove(temp_file_path)

        return {"name": file.name, "content": split_model.parse(content)}

    @staticmethod
    def handle_pdf_content(file, pdf_document):
        # 第一步:收集所有字体大小
        font_sizes = []
        page_lines = []
        for page in pdf_document.pages:
            lines = PdfSplitHandle.extract_page_lines(page)
            page_lines.append(lines)
            for line_text, font_size in lines:
                if line_text and font_size > 0:
                    font_sizes.append(font_size)

        # 计算正文字体大小(众数)
        if not font_sizes:
            body_font_size = 12
        else:
            from collections import Counter

            body_font_size = Counter(font_sizes).most_common(1)[0][0]

        # 第二步:提取内容
        content = ""
        for page_num, page in enumerate(pdf_document.pages):
            start_time = time.time()

            for text, font_size in page_lines[page_num]:
                if not text:
                    continue

                # 根据与正文字体的差值判断
                size_diff = font_size - body_font_size

                if size_diff > 2:  # 明显大于正文
                    content += f"## {text}\n\n"
                elif size_diff > 0.5:  # 略大于正文
                    content += f"### {text}\n\n"
                else:  # 正文
                    content += f"{text}\n"

            for image_index in range(PdfSplitHandle.get_page_image_count(page)):
                content += f"![image](image_{page_num}_{image_index})\n\n"

            content = content.replace("\0", "")

            elapsed_time = time.time() - start_time
            maxkb_logger.debug(
                f"File: {file.name}, Page: {page_num + 1}, Time: {elapsed_time:.3f}s"
            )

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
            toc.append((level, str(title), page_number))

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
            level, title, start_page = entry
            chapter_title = title
            # 确定结束页码，如果是最后一个章节则到文档末尾
            if i + 1 < len(toc):
                end_page = toc[i + 1][2] - 1
            else:
                end_page = len(doc.pages) - 1
            end_page = max(start_page, end_page)

            # 去掉标题中的符号
            title = PdfSplitHandle.handle_chapter_title(title)

            # 提取该章节的文本内容
            chapter_text = ""
            for page_num in range(start_page, end_page + 1):
                text = PdfSplitHandle.extract_page_text(doc.pages[page_num])
                text = re.sub(r"(?<!。)\n+", "", text)
                text = re.sub(r"(?<!.)\n+", "", text)
                # print(f'title: {title}')

                idx = text.find(title)
                if idx > -1:
                    text = text[idx + len(title) :]

                if i + 1 < len(toc):
                    _level, next_title, next_start_page = toc[i + 1]
                    next_title = PdfSplitHandle.handle_chapter_title(next_title)
                    # print(f'next_title: {next_title}')
                    idx = text.find(next_title)
                    if idx > -1:
                        text = text[:idx]

                chapter_text += text  # 提取文本

            # Null characters are not allowed.
            chapter_text = chapter_text.replace("\0", "")
            # 限制标题长度
            real_chapter_title = chapter_title[:256]
            # 限制章节内容长度
            if 0 < limit < len(chapter_text):
                split_text = smart_split_paragraph(chapter_text, limit)
                for text in split_text:
                    chapters.append({"title": real_chapter_title, "content": text})
            else:
                chapters.append(
                    {
                        "title": real_chapter_title,
                        "content": chapter_text if chapter_text else real_chapter_title,
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
        for page_num, page in enumerate(doc.pages):
            links = PdfSplitHandle.get_internal_links(doc, page)
            # 如果目录开始页码未设置，则设置为当前页码
            if len(links) > 0 and toc_start_page < 0:
                toc_start_page = page_num
            if toc_start_page < 0:
                page_content += PdfSplitHandle.extract_page_text(page)
            # 检查该页是否包含内部链接（即指向文档内部的页面）
            for num in range(len(links)):
                link = links[num]
                # 获取链接目标的页面
                dest_page = link["page"]
                rect = link["from"]  # 获取链接的矩形区域
                # 如果目录开始页码包括前言部分，则不处理前言部分
                if dest_page < toc_start_page:
                    handle_pre_toc = False

                # 提取链接区域的文本作为标题
                link_title = PdfSplitHandle.extract_link_title(page, rect)
                if not link_title:
                    link_title = PdfSplitHandle.extract_first_line(doc.pages[dest_page])
                # 提取目标页面内容作为章节开始
                start_page = dest_page
                end_page = dest_page
                # 下一个link
                next_link = links[num + 1] if num + 1 < len(links) else None
                next_link_title = None
                if next_link is not None:
                    next_link_title = PdfSplitHandle.extract_link_title(
                        page, next_link["from"]
                    )
                    if not next_link_title:
                        next_link_title = PdfSplitHandle.extract_first_line(
                            doc.pages[next_link["page"]]
                        )
                    end_page = next_link["page"]

                # 提取章节内容
                chapter_text = ""
                for p_num in range(start_page, min(end_page, len(doc.pages) - 1) + 1):
                    text = PdfSplitHandle.extract_page_text(doc.pages[p_num])
                    text = re.sub(r"(?<!。)\n+", "", text)
                    text = re.sub(r"(?<!.)\n+", "", text)

                    idx = text.find(link_title)
                    if idx > -1:
                        text = text[idx + len(link_title) :]

                    if next_link_title is not None:
                        idx = text.find(next_link_title)
                        if idx > -1:
                            text = text[:idx]
                    chapter_text += text

                # Null characters are not allowed.
                chapter_text = chapter_text.replace("\0", "")

                # 限制章节内容长度
                if 0 < limit < len(chapter_text):
                    split_text = smart_split_paragraph(chapter_text, limit)
                    for text in split_text:
                        chapters.append({"title": link_title, "content": text})
                else:
                    # 保存章节信息
                    chapters.append({"title": link_title, "content": chapter_text})

        # 目录中没有前言部分，手动处理
        if handle_pre_toc:
            pre_toc = []
            lines = page_content.strip().split("\n")
            try:
                for line in lines:
                    if re.match(r"^前\s*言", line):
                        pre_toc.append({"title": line, "content": ""})
                    else:
                        pre_toc[-1]["content"] += line
                for i in range(len(pre_toc)):
                    pre_toc[i]["content"] = re.sub(
                        r"(?<!。)\n+", "", pre_toc[i]["content"]
                    )
                    pre_toc[i]["content"] = re.sub(
                        r"(?<!.)\n+", "", pre_toc[i]["content"]
                    )
            except BaseException as e:
                maxkb_logger.error(
                    _(
                        "This document has no preface and is treated as ordinary text: {e}"
                    ).format(e=e)
                )
                if pattern_list is not None and len(pattern_list) > 0:
                    split_model = SplitModel(pattern_list, with_filter, limit)
                else:
                    split_model = SplitModel(
                        default_pattern_list, with_filter=with_filter, limit=limit
                    )
                # 插入目录前的部分
                page_content = re.sub(r"(?<!。)\n+", "", page_content)
                page_content = re.sub(r"(?<!.)\n+", "", page_content)
                page_content = page_content.strip()
                pre_toc = split_model.parse(page_content)
            chapters = pre_toc + chapters
        return chapters

    @staticmethod
    def get_internal_links(doc, page):
        links = []
        annotations = getattr(page, "annotations", None) or []
        for annotation in annotations:
            annotation = get_pdf_object(annotation)
            if not hasattr(annotation, "get"):
                continue
            if annotation.get("/Subtype") != "/Link":
                continue
            dest_page = PdfSplitHandle.get_annotation_destination_page_number(
                doc, annotation
            )
            if dest_page is None or dest_page < 0 or dest_page >= len(doc.pages):
                continue
            rect = annotation.get("/Rect")
            links.append(
                {"page": dest_page, "from": PdfSplitHandle.normalize_rect(rect)}
            )
        return links

    @staticmethod
    def get_annotation_destination_page_number(doc, annotation):
        destination = annotation.get("/Dest")
        if destination is None:
            action = get_pdf_object(annotation.get("/A"))
            if hasattr(action, "get") and action.get("/S") == "/GoTo":
                destination = action.get("/D")
        return PdfSplitHandle.get_destination_page_number(doc, destination)

    @staticmethod
    def get_destination_page_number(doc, destination):
        if destination is None:
            return None

        destination = get_pdf_object(destination)

        if isinstance(destination, bytes):
            destination = destination.decode(errors="ignore")

        if isinstance(destination, str):
            destination = doc.named_destinations.get(destination)
            if destination is None:
                return None

        if isinstance(destination, Destination):
            try:
                page_number = doc.get_destination_page_number(destination)
                return page_number if page_number >= 0 else None
            except BaseException:
                return None

        if isinstance(destination, (list, tuple)) and len(destination) > 0:
            return PdfSplitHandle.get_page_number_by_reference(doc, destination[0])

        if hasattr(destination, "get") and destination.get("/D") is not None:
            return PdfSplitHandle.get_destination_page_number(
                doc, destination.get("/D")
            )

        return None

    @staticmethod
    def get_page_number_by_reference(doc, page_reference):
        try:
            page_number = int(page_reference)
            if 0 <= page_number < len(doc.pages):
                return page_number
        except BaseException:
            pass

        try:
            page = get_pdf_object(page_reference)
            page_number = doc.get_page_number(page)
            return page_number if page_number >= 0 else None
        except BaseException:
            return None

    @staticmethod
    def normalize_rect(rect):
        if rect is None or len(rect) < 4:
            return None
        left, bottom, right, top = [float(value) for value in rect[:4]]
        return min(left, right), min(bottom, top), max(left, right), max(bottom, top)

    @staticmethod
    def extract_link_title(page, rect):
        if rect is None:
            return ""

        left, bottom, right, top = rect
        tolerance = 2
        text_parts = []

        def visitor_text(text, cm, tm, font_dict, font_size):
            if not text:
                return
            x = tm[4] if len(tm) > 4 else 0
            y = tm[5] if len(tm) > 5 else 0
            text_top = y + (float(font_size) if font_size else 0)
            in_horizontal_range = left - tolerance <= x <= right + tolerance
            in_vertical_range = (
                bottom - tolerance <= y <= top + tolerance
                or bottom - tolerance <= text_top <= top + tolerance
            )
            if in_horizontal_range and in_vertical_range:
                text_parts.append(text)

        try:
            page.extract_text(visitor_text=visitor_text)
        except BaseException:
            return ""

        return "".join(text_parts).strip().split("\n")[0].replace(".", "").strip()

    @staticmethod
    def extract_first_line(page):
        text = PdfSplitHandle.extract_page_text(page).strip()
        return text.split("\n")[0].replace(".", "").strip() if text else ""

    @staticmethod
    def handle_chapter_title(title):
        title = re.sub(r"[一二三四五六七八九十\s*]、\s*", "", title)
        title = re.sub(r"第[一二三四五六七八九十]章\s*", "", title)
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

        try:
            with open(temp_file_path, "rb") as pdf_file:
                pdf_document = PdfReader(pdf_file)
                return self.handle_pdf_content(file, pdf_document)
        except BaseException as e:
            traceback.print_exception(e)
            return f"{e}"
        finally:
            os.remove(temp_file_path)
