from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants
from common.result import result
from tools.api.tool import ToolCreateAPI
from tools.serializers.tool import ToolSerializer


class ToolCreateView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(methods=['POST'],
                   description=_('Create tool'),
                   operation_id=_('Create tool'),
                   request=ToolCreateAPI.get_request(),
                   responses=ToolCreateAPI.get_response(),
                   tags=[_('Tool')])
    @has_permissions(PermissionConstants.TOOL_CREATE)
    # @log(menu='Tool', operate="Create tool",
    #      get_operation_object=lambda r, k: r.data.get('name'))
    def post(self, request: Request, workspace_id: str):
        print(workspace_id)
        return result.success(ToolSerializer.Create(data={'user_id': request.user.id}).insert(request.data))
