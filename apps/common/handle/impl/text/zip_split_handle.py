# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： text_split_handle.py
    @date：2024/3/27 18:19
    @desc:
"""
import io
import os
import re
import zipfile
from typing import List
from urllib.parse import urljoin

import uuid_utils.compat as uuid
from charset_normalizer import detect
from django.utils.translation import gettext_lazy as _

from common.handle.base_split_handle import BaseSplitHandle
from common.handle.impl.text.csv_split_handle import CsvSplitHandle
from common.handle.impl.text.doc_split_handle import DocSplitHandle
from common.handle.impl.text.html_split_handle import HTMLSplitHandle
from common.handle.impl.text.pdf_split_handle import PdfSplitHandle
from common.handle.impl.text.text_split_handle import TextSplitHandle
from common.handle.impl.text.xls_split_handle import XlsSplitHandle
from common.handle.impl.text.xlsx_split_handle import XlsxSplitHandle
from common.utils.common import parse_md_image
from knowledge.models import File


class FileBufferHandle:
    buffer = None

    def get_buffer(self, file):
        if self.buffer is None:
            self.buffer = file.read()
        return self.buffer


default_split_handle = TextSplitHandle()
split_handles = [
    HTMLSplitHandle(),
    DocSplitHandle(),
    PdfSplitHandle(),
    XlsxSplitHandle(),
    XlsSplitHandle(),
    CsvSplitHandle(),
    default_split_handle
]


def file_to_paragraph(file, pattern_list: List, with_filter: bool, limit: int, save_inner_image):
    get_buffer = FileBufferHandle().get_buffer
    for split_handle in split_handles:
        if split_handle.support(file, get_buffer):
            return split_handle.handle(file, pattern_list, with_filter, limit, get_buffer, save_inner_image)
    raise Exception(_('Unsupported file format'))


def is_valid_uuid(uuid_str: str):
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        return False
    return True


def get_image_list(result_list: list, zip_files: List[str]):
    image_file_list = []
    for result in result_list:
        for p in result.get('content', []):
            content: str = p.get('content', '')
            image_list = parse_md_image(content)
            for image in image_list:
                search = re.search("\(.*\)", image)
                if search:
                    new_image_id = str(uuid.uuid7())
                    source_image_path = search.group().replace('(', '').replace(')', '')
                    source_image_path = source_image_path.strip().split(" ")[0]
                    image_path = urljoin(result.get('name'), '.' + source_image_path if source_image_path.startswith(
                        '/') else source_image_path)
                    if not zip_files.__contains__(image_path):
                        continue
                    if image_path.startswith('oss/file/') or image_path.startswith('oss/image/'):
                        image_id = image_path.replace('oss/file/', '').replace('oss/file/', '')
                        if is_valid_uuid(image_id):
                            image_file_list.append({'source_file': image_path,
                                                    'image_id': image_id})
                        else:
                            image_file_list.append({'source_file': image_path,
                                                    'image_id': new_image_id})
                            content = content.replace(source_image_path, f'./oss/file/{new_image_id}')
                            p['content'] = content
                    else:
                        image_file_list.append({'source_file': image_path,
                                                'image_id': new_image_id})
                        content = content.replace(source_image_path, f'./oss/file/{new_image_id}')
                        p['content'] = content

    return image_file_list


def get_file_name(file_name):
    try:
        file_name_code = file_name.encode('cp437')
        charset = detect(file_name_code)['encoding']
        return file_name_code.decode(charset)
    except Exception as e:
        return file_name


def filter_image_file(result_list: list, image_list):
    image_source_file_list = [image.get('source_file') for image in image_list]
    return [r for r in result_list if not image_source_file_list.__contains__(r.get('name', ''))]


class ZipSplitHandle(BaseSplitHandle):
    def handle(self, file, pattern_list: List, with_filter: bool, limit: int, get_buffer, save_image):
        if type(limit) is str:
            limit = int(limit)
        if type(with_filter) is str:
            with_filter = with_filter.lower() == 'true'
        buffer = get_buffer(file)
        bytes_io = io.BytesIO(buffer)
        result = []
        # 打开zip文件
        with zipfile.ZipFile(bytes_io, 'r') as zip_ref:
            # 获取压缩包中的文件名列表
            files = zip_ref.namelist()
            # 读取压缩包中的文件内容
            for file in files:
                if file.endswith('/') or file.startswith('__MACOSX'):
                    continue
                with zip_ref.open(file) as f:
                    # 对文件内容进行处理
                    try:
                        # 处理一下文件名
                        f.name = get_file_name(f.name)
                        value = file_to_paragraph(f, pattern_list, with_filter, limit, save_image)
                        if isinstance(value, list):
                            result = [*result, *value]
                        else:
                            result.append(value)
                    except Exception:
                        pass
            image_list = get_image_list(result, files)
            result = filter_image_file(result, image_list)
            image_mode_list = []
            for image in image_list:
                with zip_ref.open(image.get('source_file')) as f:
                    i = File(
                        id=image.get('image_id'),
                        file_name=os.path.basename(image.get('source_file')),
                        meta={'debug': False, 'content': f.read()}  # 这里的content是二进制数据
                    )
                    image_mode_list.append(i)
            save_image(image_mode_list)
        return result

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".zip") or file_name.endswith(".ZIP"):
            return True
        return False

    def get_content(self, file, save_image):
        """
        从 zip 中提取并返回拼接的 md 文本，同时收集并保存内嵌图片（通过 save_image 回调）。
        使用 posixpath 来正确处理 zip 内部的路径拼接与规范化。
        """
        buffer = file.read() if hasattr(file, 'read') else None
        bytes_io = io.BytesIO(buffer) if buffer is not None else io.BytesIO(file)
        md_items = []  # 存储 (md_text, source_file_path)
        image_mode_list = []

        import posixpath

        def is_image_name(name: str):
            ext = posixpath.splitext(name.lower())[1]
            return ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')

        with zipfile.ZipFile(bytes_io, 'r') as zip_ref:
            files = zip_ref.namelist()
            for inner_name in files:
                if inner_name.endswith('/') or inner_name.startswith('__MACOSX'):
                    continue
                with zip_ref.open(inner_name) as zf:
                    try:
                        real_name = get_file_name(zf.name)
                    except Exception:
                        real_name = zf.name
                    raw = zf.read()
                    # 图片直接收集
                    if is_image_name(real_name):
                        image_id = str(uuid.uuid7())
                        fmodel = File(
                            id=image_id,
                            file_name=os.path.basename(real_name),
                            meta={'debug': False, 'content': raw}
                        )
                        image_mode_list.append(fmodel)
                        continue

                    # 为 split_handle 提供可重复读取的 file-like 对象
                    inner_file = io.BytesIO(raw)
                    inner_file.name = real_name

                    # 尝试使用已注册的 split handle 的 get_content
                    md_text = None
                    for split_handle in split_handles:
                        # 准备一个简单的 get_buffer 回调，返回当前 raw
                        get_buffer = lambda f, _raw=raw: _raw
                        if split_handle.support(inner_file, get_buffer):
                            inner_file.seek(0)
                            md_text = split_handle.get_content(inner_file, save_image)
                            break

                    # 如果没有任何 split_handle 处理，按文本解码作为后备
                    if md_text is None:
                        enc = detect(raw).get('encoding') or 'utf-8'
                        try:
                            md_text = raw.decode(enc, errors='ignore')
                        except Exception:
                            md_text = raw.decode('utf-8', errors='ignore')

                    if isinstance(md_text, str) and md_text.strip():
                        # 保存 md 文本与其所在的文件路径，后面统一做图片路径替换
                        md_items.append((md_text, real_name))

            # 将收集到的图片通过回调保存（一次性）
            if image_mode_list:
                save_image(image_mode_list)

        # 后处理：在每个 md 片段中将相对/绝对引用替换为已保存图片的 oss 路径
        content_parts = []
        for md_text, base_name in md_items:
            image_refs = parse_md_image(md_text)
            for image in image_refs:
                search = re.search(r"\(.*\)", image)
                if not search:
                    continue
                source_image_path = search.group().strip("()").split(" ")[0]

                # 规范化 zip 内部路径：若以 '/' 开头，视为相对于 zip 根，否则相对于 base_name 的目录
                if source_image_path.startswith('/'):
                    joined = posixpath.normpath(source_image_path.lstrip('/'))
                else:
                    base_dir = posixpath.dirname(base_name)
                    joined = posixpath.normpath(posixpath.join(base_dir, source_image_path))

                # 匹配已收集图片：以文件名做匹配（zip 中的文件名通常是不含反斜杠的 POSIX 风格）
                matched = None
                for img_model in image_mode_list:
                    if img_model.file_name == posixpath.basename(joined):
                        matched = img_model
                        break

                if matched:
                    md_text = md_text.replace(source_image_path, f'./oss/file/{matched.id}')

            content_parts.append(md_text)

        return '\n\n'.join(content_parts)


