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
        return ""
