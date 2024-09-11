# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： tools.py
    @date：2024/9/11 16:41
    @desc:
"""
import io
import uuid
from functools import reduce
from io import BytesIO
from xml.etree.ElementTree import fromstring
from zipfile import ZipFile

from PIL import Image as PILImage
from openpyxl.drawing.image import Image as openpyxl_Image
from openpyxl.packaging.relationship import get_rels_path, get_dependents
from openpyxl.xml.constants import SHEET_DRAWING_NS, REL_NS, SHEET_MAIN_NS

from common.handle.base_parse_qa_handle import get_title_row_index_dict, get_row_value
from dataset.models import Image


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
            print(e)
            continue
        image.embed = dep.id  # 文件rId
        image.target = dep.target  # 文件地址
        images.append(image)
    return images


def xlsx_embed_cells_images(buffer) -> {}:
    archive = ZipFile(buffer)
    # 解析cellImage.xml文件
    deps = get_dependents(archive, get_rels_path("xl/cellimages.xml"))
    image_rel = handle_images(deps=deps, archive=archive)
    # 工作表及其中图片ID
    sheet_list = {}
    for item in archive.namelist():
        if not item.startswith('xl/worksheets/sheet'):
            continue
        key = item.split('/')[-1].split('.')[0].split('sheet')[-1]
        sheet_list[key] = parse_element_sheet_xml(fromstring(archive.read(item)))
    cell_images_xml = parse_element(fromstring(archive.read("xl/cellimages.xml")))
    cell_images_rel = {}
    for image in image_rel:
        cell_images_rel[image.embed] = image
    for cnv, embed in cell_images_xml.items():
        cell_images_xml[cnv] = cell_images_rel.get(embed)
    result = {}
    for key, img in cell_images_xml.items():
        image_excel_id_list = [_xl for _xl in
                               reduce(lambda x, y: [*x, *y], [sheet for sheet_id, sheet in sheet_list.items()], []) if
                               key in _xl]
        if len(image_excel_id_list) > 0:
            image_excel_id = image_excel_id_list[-1]
            f = archive.open(img.target)
            img_byte = io.BytesIO()
            im = PILImage.open(f).convert('RGB')
            im.save(img_byte, format='JPEG')
            image = Image(id=uuid.uuid1(), image=img_byte.getvalue(), image_name=img.path)
            result['=' + image_excel_id] = image
    archive.close()
    return result


