import io
from pathlib import Path
from urllib.parse import quote

import openpyxl
import xlrd
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from common.exception.app_exception import AppApiException
from knowledge.models import Knowledge
from knowledge.serializers.tag import TagCreateSerializer, TagSerializers


TAG_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "template" / "tags_template.xlsx"
TAG_TEMPLATE_CONTENT_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class TagImportFileSerializer(serializers.Serializer):
    file = serializers.FileField(required=True, label=_("文件"))


def cell_text(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def parse_tag_sheet(sheet_name, rows):
    rows = iter(rows)
    headers = [cell_text(value) for value in next(rows, ())]
    while headers and not headers[-1]:
        headers.pop()
    if not headers and not any(any(cell_text(value) for value in row) for row in rows):
        return []
    if headers != ["标签", "标签值"]:
        raise AppApiException(
            500, _("工作表“%(sheet)s”的表头必须为“标签、标签值”，请使用标签模板") % {"sheet": sheet_name}
        )

    tags = []
    for row_number, row in enumerate(rows, start=2):
        values = [cell_text(value) for value in row]
        if not any(values):
            continue
        if any(values[2:]):
            raise AppApiException(
                500,
                _("工作表“%(sheet)s”第 %(row)s 行只能包含标签和标签值") % {"sheet": sheet_name, "row": row_number},
            )
        values += [""] * (2 - len(values))
        serializer = TagCreateSerializer(data={"key": values[0], "value": values[1]})
        if not serializer.is_valid():
            field_names = {"key": _("标签"), "value": _("标签值")}
            message = "；".join(
                f"{field_names[field]}：{'、'.join(map(str, errors))}" for field, errors in serializer.errors.items()
            )
            raise AppApiException(
                500,
                _("工作表“%(sheet)s”第 %(row)s 行：%(message)s")
                % {"sheet": sheet_name, "row": row_number, "message": message},
            )
        tags.append(dict(serializer.validated_data))
    return tags


def parse_tag_file(file):
    extension = Path(file.name).suffix.lower()
    if extension not in (".xls", ".xlsx"):
        raise AppApiException(500, _("仅支持上传 XLS、XLSX 格式的文件"))

    workbook = None
    try:
        content = file.read()
        if extension == ".xlsx":
            workbook = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
            sheets = ((sheet.title, sheet.iter_rows(values_only=True)) for sheet in workbook.worksheets)
        else:
            workbook = xlrd.open_workbook(file_contents=content, on_demand=True)
            sheets = (
                (sheet.name, (sheet.row_values(index) for index in range(sheet.nrows))) for sheet in workbook.sheets()
            )
        tags = []
        for sheet_name, rows in sheets:
            tags.extend(parse_tag_sheet(sheet_name, rows))
    except AppApiException:
        raise
    except Exception as exc:
        raise AppApiException(500, _("文件无法读取，请上传有效的 XLS 或 XLSX 文件")) from exc
    finally:
        if workbook is not None:
            if extension == ".xlsx":
                workbook.close()
            else:
                workbook.release_resources()

    if not tags:
        raise AppApiException(500, _("文件中没有可导入的标签"))
    return tags


class TagImportSerializers(serializers.Serializer):
    workspace_id = serializers.CharField(required=True, label=_("Workspace ID"))
    knowledge_id = serializers.UUIDField(required=True, label=_("Knowledge ID"))

    def is_valid(self, *, raise_exception=False):
        valid = super().is_valid(raise_exception=raise_exception)
        if valid:
            if (
                not QuerySet(Knowledge)
                .filter(id=self.validated_data["knowledge_id"], workspace_id=self.validated_data["workspace_id"])
                .exists()
            ):
                raise AppApiException(500, _("Knowledge id does not exist"))
        return valid

    @transaction.atomic
    def import_tags(self, instance):
        self.is_valid(raise_exception=True)
        upload = TagImportFileSerializer(data=instance)
        upload.is_valid(raise_exception=True)
        tags = parse_tag_file(upload.validated_data["file"])
        return TagSerializers.Create(data={**self.validated_data, "tags": tags}).insert()

    def export_template(self):
        self.is_valid(raise_exception=True)
        response = HttpResponse(TAG_TEMPLATE_PATH.read_bytes(), content_type=TAG_TEMPLATE_CONTENT_TYPE)
        response["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote('标签模板.xlsx')}"
        return response
