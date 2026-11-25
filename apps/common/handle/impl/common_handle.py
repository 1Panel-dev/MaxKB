# coding=utf-8
"""
@project: MaxKB
@Author：虎
@file： tools.py
@date：2024/9/11 16:41
@desc:
"""

import traceback
from collections import defaultdict
from io import BytesIO
from itertools import chain
from xml.etree.ElementTree import fromstring
from zipfile import ZipFile

import uuid_utils.compat as uuid
from PIL import Image as PILImage
from PIL import ImageFile
from openpyxl.drawing.image import Image as openpyxl_Image
from openpyxl.packaging.relationship import get_rels_path, get_dependents
from openpyxl.xml.constants import MAX_COLUMN, MAX_ROW, SHEET_DRAWING_NS, REL_NS, SHEET_MAIN_NS

from common.utils.logger import maxkb_logger
from knowledge.models import File

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


def _formula_image_references(archive):
    manifest = "xl/cellimages.xml"
    members = set(archive.namelist())
    if manifest not in members or get_rels_path(manifest) not in members:
        return
    deps = get_dependents(archive, get_rels_path(manifest))
    images = {image.embed: image for image in handle_images(deps, archive)}
    formulas = {
        formula
        for name in archive.namelist()
        if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        for formula in parse_element_sheet_xml(fromstring(archive.read(name)))
        if isinstance(formula, str)
    }
    for key, embed in parse_element(fromstring(archive.read(manifest))).items():
        if embed in images:
            for formula in formulas:
                if key in formula:
                    yield "=" + formula, images[embed]


def _drawing_image_references(workbook):
    for sheet in workbook.worksheets:
        for image in sheet._images:
            # Both one-cell and two-cell anchors use a zero-based start marker.
            start = getattr(image.anchor, "_from", None)
            if start is not None and 0 <= start.row < MAX_ROW and 0 <= start.col < MAX_COLUMN:
                yield (sheet.title, start.row + 1, start.col + 1), image


def read_xlsx_images(buffer, workbook=None, save_image=None):
    formula_images = {}
    drawing_images = defaultdict(dict)
    files = {}
    total_pixels = 0
    with ZipFile(buffer) as archive:
        validate_xlsx_archive(archive)
        references = _formula_image_references(archive)
        if workbook is not None:
            references = chain(references, _drawing_image_references(workbook))
        for position, image in references:
            content = image.ref.getvalue()
            if content not in files:
                pixels = image.width * image.height
                if pixels > MAX_EMBED_IMAGE_PIXELS or total_pixels + pixels > MAX_EMBED_IMAGE_AGGREGATE_PIXELS:
                    maxkb_logger.warning(f"Skipping embedded image exceeding pixel limit: {image.width}x{image.height}")
                    continue
                total_pixels += pixels
                try:
                    encoded = BytesIO()
                    with PILImage.open(BytesIO(content)) as decoded:
                        decoded.convert("RGB").save(encoded, format="JPEG")
                    files[content] = File(
                        id=uuid.uuid7(), file_name="image.jpg", meta={"debug": False, "content": encoded.getvalue()}
                    )
                except Exception as exc:
                    maxkb_logger.warning(f"Error decoding embedded XLSX image: {exc}")
                    continue
            if isinstance(position, str):
                formula_images[position] = files[content]
            else:
                sheet, row, column = position
                drawing_images[sheet].setdefault((row, column), []).append(files[content])
    if files and save_image is not None:
        save_image(list(files.values()))
    return formula_images, drawing_images


def xlsx_embed_cells_images(buffer, save_image=None):
    formula_images, _ = read_xlsx_images(buffer, save_image=save_image)
    return formula_images
