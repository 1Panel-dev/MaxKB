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
import uuid
import zipfile
from typing import List
from urllib.parse import urljoin

from django.db.models import QuerySet

from common.handle.base_parse_qa_handle import BaseParseQAHandle
from common.handle.impl.qa.csv_parse_qa_handle import CsvParseQAHandle
from common.handle.impl.qa.xls_parse_qa_handle import XlsParseQAHandle
from common.handle.impl.qa.xlsx_parse_qa_handle import XlsxParseQAHandle
from common.util.common import parse_md_image
from dataset.models import Image
from django.utils.translation import gettext_lazy as _

class FileBufferHandle:
    buffer = None

    def get_buffer(self, file):
        if self.buffer is None:
            self.buffer = file.read()
        return self.buffer


split_handles = [XlsParseQAHandle(), XlsxParseQAHandle(), CsvParseQAHandle()]


def save_inner_image(image_list):
    """
    子模块插入图片逻辑
    @param image_list:
    @return:
    """
    if image_list is not None and len(image_list) > 0:
        QuerySet(Image).bulk_create(image_list)


def file_to_paragraph(file):
    """
    文件转换为段落列表
    @param file: 文件
    @return: {
      name:文件名
      paragraphs:段落列表
    }
    """
    get_buffer = FileBufferHandle().get_buffer
    for split_handle in split_handles:
        if split_handle.support(file, get_buffer):
            return split_handle.handle(file, get_buffer, save_inner_image)
    raise Exception(_("Unsupported file format"))


def is_valid_uuid(uuid_str: str):
    """
    校验字符串是否是uuid
    @param uuid_str: 需要校验的字符串
    @return: bool
    """
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        return False
    return True


def get_image_list(result_list: list, zip_files: List[str]):
    """
    获取图片文件列表
    @param result_list:
    @param zip_files:
    @return:
    """
    image_file_list = []
    for result in result_list:
        for p in result.get('paragraphs', []):
            content: str = p.get('content', '')
            image_list = parse_md_image(content)
            for image in image_list:
                search = re.search("\(.*\)", image)
                if search:
                    new_image_id = str(uuid.uuid1())
                    source_image_path = search.group().replace('(', '').replace(')', '')
                    image_path = urljoin(result.get('name'), '.' + source_image_path if source_image_path.startswith(
                        '/') else source_image_path)
                    if not zip_files.__contains__(image_path):
                        continue
                    if image_path.startswith('api/file/') or image_path.startswith('api/image/'):
                        image_id = image_path.replace('api/file/', '').replace('api/image/', '')
                        if is_valid_uuid(image_id):
                            image_file_list.append({'source_file': image_path,
                                                    'image_id': image_id})
                        else:
                            image_file_list.append({'source_file': image_path,
                                                    'image_id': new_image_id})
                            content = content.replace(source_image_path, f'/api/image/{new_image_id}')
                            p['content'] = content
                    else:
                        image_file_list.append({'source_file': image_path,
                                                'image_id': new_image_id})
                        content = content.replace(source_image_path, f'/api/image/{new_image_id}')
                        p['content'] = content

    return image_file_list


def filter_image_file(result_list: list, image_list):
    image_source_file_list = [image.get('source_file') for image in image_list]
    return [r for r in result_list if not image_source_file_list.__contains__(r.get('name', ''))]


class ZipParseQAHandle(BaseParseQAHandle):

    def handle(self, file, get_buffer, save_image):
        buffer = get_buffer(file)
        bytes_io = io.BytesIO(buffer)
        result = []
        # 打开zip文件
        with zipfile.ZipFile(bytes_io, 'r') as zip_ref:
            # 获取压缩包中的文件名列表
            files = zip_ref.namelist()
            # 读取压缩包中的文件内容
            for file in files:
                # 跳过 macOS 特有的元数据目录和文件
                if file.endswith('/') or file.startswith('__MACOSX'):
                    continue
                with zip_ref.open(file) as f:
                    # 对文件内容进行处理
                    try:
                        value = file_to_paragraph(f)
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
                    i = Image(id=image.get('image_id'), image=f.read(),
                              image_name=os.path.basename(image.get('source_file')))
                    image_mode_list.append(i)
            save_image(image_mode_list)
        return result

    def support(self, file, get_buffer):
        file_name: str = file.name.lower()
        if file_name.endswith(".zip") or file_name.endswith(".ZIP"):
            return True
        return False
