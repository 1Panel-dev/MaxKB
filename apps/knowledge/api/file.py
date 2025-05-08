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
                        'format': 'binary'  # Tells Swagger it's a file
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
