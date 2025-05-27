from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter

from common.mixins.api_mixin import APIMixin


class ApplicationKeyCreateAPI(APIMixin):
    @staticmethod
    def get_parameters():
        return [
            OpenApiParameter(
                name="workspace_id",
                description="工作空间id",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            ),
            OpenApiParameter(
                name="application_id",
                description="application ID",
                type=OpenApiTypes.STR,
                location='path',
                required=True,
            )
        ]

    # class Operate(APIMixin):
    #     @staticmethod
    #     def s():
    #         pass

   # def get_response():
   #     return ApplicationKeyCreateResponse
