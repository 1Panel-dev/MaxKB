from drf_spectacular.types import OpenApiTypes

from knowledge.api.tag import TagCreateAPI
from knowledge.serializers.tag_import import TAG_TEMPLATE_CONTENT_TYPE


class TagImportAPI(TagCreateAPI):
    @staticmethod
    def get_request():
        return {
            "multipart/form-data": {
                "type": "object",
                "required": ["file"],
                "properties": {
                    "file": {"type": "string", "format": "binary", "description": "标签导入文件（XLS、XLSX）"}
                },
            }
        }


class TagTemplateExportAPI(TagCreateAPI):
    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_response():
        return {(200, TAG_TEMPLATE_CONTENT_TYPE): OpenApiTypes.BINARY}
