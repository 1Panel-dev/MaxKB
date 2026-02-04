from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin
from common.result import DefaultResultSerializer


class FileUploadAPI(APIMixin):

    @staticmethod
    def get_request():
        return {
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': '要上传的文件'

                    },
                    "source_id": {
                        'type': 'string',
                        'description': '资源id 如果source_type为[TEMPORARY_30_MINUTE,TEMPORARY_120_MINUTE,TEMPORARY_1_DAY,SYSTEM] 其他的需要为对应资源的id'
                    },
                    "source_type": {
                        'type': 'string',
                        'description': '资源类型[KNOWLEDGE,APPLICATION,TOOL,DOCUMENT,CHAT,SYSTEM,TEMPORARY_30_MINUTE,TEMPORARY_120_MINUTE,TEMPORARY_1_DAY]'
                    }
                }
            }
        }

    @staticmethod
    def get_response():
        return DefaultResultSerializer


class FileGetAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="file_id",
                description="文件id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
        ]

    @staticmethod
    def get_response():
        return DefaultResultSerializer
