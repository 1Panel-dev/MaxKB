# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： tools.py
@date：2024/9/11 16:41
@desc:
"""

import io
import traceback
from io import BytesIO
from xml.etree.ElementTree import fromstring
from zipfile import ZipFile

import uuid_utils.compat as uuid
from PIL import Image as PILImage
from openpyxl.drawing.image import Image as openpyxl_Image
from openpyxl.packaging.relationship import get_rels_path, get_dependents
from openpyxl.xml.constants import SHEET_DRAWING_NS, REL_NS, SHEET_MAIN_NS

from common.utils.logger import maxkb_logger
from knowledge.models import File

from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True

# 全局图片解码像素上限（不再禁用 Pillow 的解压炸弹保护）。
# 超过该上限 Pillow 会告警，超过 2 倍会直接抛错，避免超大图片耗尽 worker 内存。
PILImage.MAX_IMAGE_PIXELS = 50_000_000

# 内嵌图片解码保护（防解压炸弹 / 超大尺寸图片导致共享 worker OOM）。
MAX_EMBED_IMAGE_PIXELS = 16_000_000
MAX_EMBED_IMAGE_AGGREGATE_PIXELS = 64_000_000

# XLSX(zip) 压缩包防护，限制成员数 / 解压后总大小 / 解压膨胀比。
MAX_EMBED_ARCHIVE_MEMBERS = 10_000
MAX_EMBED_ARCHIVE_UNCOMPRESSED_BYTES = 1024 * 1024 * 1024
MAX_EMBED_ARCHIVE_EXPANSION_RATIO = 50


def validate_xlsx_archive(archive: ZipFile):
    infolist = archive.infolist()
    if len(infolist) > MAX_EMBED_ARCHIVE_MEMBERS:
        raise ValueError(f"XLSX archive member count exceeds limit: {len(infolist)}")
    total_uncompressed = sum(info.file_size for info in infolist)
    total_compressed = sum(info.compress_size for info in infolist)
    if total_uncompressed > MAX_EMBED_ARCHIVE_UNCOMPRESSED_BYTES:
        raise ValueError("XLSX archive uncompressed size exceeds limit")
    if total_compressed > 0 and total_uncompressed > total_compressed * MAX_EMBED_ARCHIVE_EXPANSION_RATIO:
        raise ValueError("XLSX archive expansion ratio exceeds limit")


def validate_xlsx_buffer(buffer):
    archive = ZipFile(buffer)
    try:
        validate_xlsx_archive(archive)
    finally:
        archive.close()


def parse_element(element) -> {}:
    data = {}
    xdr_namespace = "{%s}" % SHEET_DRAWING_NS
    targets = level_order_traversal(element, xdr_namespace + "nvPicPr")
    for target in targets:
        cNvPr = embed = ""
        for child in target:
            if child.tag == xdr_namespace + "nvPicPr":
                cNvPr = child[0].attrib["name"]
            elif child.tag == xdr_namespace + "blipFill":
                _rel_embed = "{%s}embed" % REL_NS
                embed = child[0].attrib[_rel_embed]
        if cNvPr:
            data[cNvPr] = embed
    return data


def parse_element_sheet_xml(element) -> []:
    data = []
    xdr_namespace = "{%s}" % SHEET_MAIN_NS
    targets = level_order_traversal(element, xdr_namespace + "f")
    for target in targets:
        for child in target:
            if child.tag == xdr_namespace + "f":
                data.append(child.text)
    return data


def level_order_traversal(root, flag: str) -> []:
    queue = [root]
    targets = []
    while queue:
        node = queue.pop(0)
        children = [child.tag for child in node]
        if flag in children:
            targets.append(node)
            continue
        for child in node:
            queue.append(child)
    return targets


def handle_images(deps, archive: ZipFile) -> []:
    images = []
    if not PILImage:  # Pillow not installed, drop images
        return images
    for dep in deps:
        try:
            image_io = archive.read(dep.target)
            image = openpyxl_Image(BytesIO(image_io))
        except Exception as e:
            maxkb_logger.error(f"Error reading image {dep.target}: {e}, {traceback.format_exc()}")
            continue
        image.embed = dep.id  # 文件rId
        image.target = dep.target  # 文件地址
        images.append(image)
    return images


def xlsx_embed_cells_images(buffer) -> {}:
    archive = ZipFile(buffer)
    validate_xlsx_archive(archive)
    # 解析cellImage.xml文件
    deps = get_dependents(archive, get_rels_path("xl/cellimages.xml"))
    image_rel = handle_images(deps=deps, archive=archive)
    # 工作表及其中图片ID
    sheet_list = {}
    for item in archive.namelist():
        if not item.startswith("xl/worksheets/sheet"):
            continue
        key = item.split("/")[-1].split(".")[0].split("sheet")[-1]
        sheet_list[key] = parse_element_sheet_xml(fromstring(archive.read(item)))
    cell_images_xml = parse_element(fromstring(archive.read("xl/cellimages.xml")))
    cell_images_rel = {}
    for image in image_rel:
        cell_images_rel[image.embed] = image
    for cnv, embed in cell_images_xml.items():
        cell_images_xml[cnv] = cell_images_rel.get(embed)
    result = {}
    total_pixels = 0
    for key, img in cell_images_xml.items():
        all_cells = [cell for _sheet_id, sheet in sheet_list.items() if sheet is not None for cell in sheet or []]

        image_excel_id_list = [cell for cell in all_cells if isinstance(cell, str) and key in cell]
        # print(key, img)
        if img is None:
            continue
        if len(image_excel_id_list) > 0:
            image_excel_id = image_excel_id_list[-1]
            f = archive.open(img.target)
            img_byte = io.BytesIO()
            try:
                with PILImage.open(f) as im:
                    width, height = im.size
                    pixels = width * height
                    if pixels > MAX_EMBED_IMAGE_PIXELS:
                        maxkb_logger.warning(
                            f"Skip oversized embedded image {img.path}: {width}x{height} pixels exceeds limit"
                        )
                        continue
                    total_pixels += pixels
                    if total_pixels > MAX_EMBED_IMAGE_AGGREGATE_PIXELS:
                        maxkb_logger.warning("Skip embedded images in archive: aggregate pixels exceed limit")
                        break
                    im.convert("RGB").save(img_byte, format="JPEG")
            except Exception as e:
                maxkb_logger.error(f"Error decoding image {img.target}: {e}, {traceback.format_exc()}")
                continue
            image = File(id=uuid.uuid7(), file_name=img.path, meta={"debug": False, "content": img_byte.getvalue()})
            result["=" + image_excel_id] = image
    archive.close()
    return result
