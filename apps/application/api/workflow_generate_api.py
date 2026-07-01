# coding=utf-8
"""
@project: MaxKB
@file： workflow_generate_api.py
@desc: 自然语言生成工作流 API（流式 SSE，实时展示生成过程）
"""
import json

from django.http import StreamingHttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.flow.workflow_generator import generate_workflow_stream
from common import result
from common.auth import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, RoleConstants


def _sse(event: dict) -> str:
    return 'data: ' + json.dumps(event, ensure_ascii=False) + '\n\n'


class WorkflowGenerateView(APIView):
    """自然语言生成工作流（流式）"""
    authentication_classes = [TokenAuth]

    @extend_schema(
        summary="自然语言生成工作流",
        description="根据自然语言描述流式生成可直接使用的工作流（SSE：stage/plan/done/error 事件）",
    )
    @has_permissions(PermissionConstants.APPLICATION_CREATE.get_workspace_permission(),
                     RoleConstants.USER.get_workspace_role(),
                     RoleConstants.WORKSPACE_MANAGE.get_workspace_role())
    def post(self, request: Request, workspace_id: str):
        description = (request.data.get("description") or '').strip()
        model_id = request.data.get("model_id")
        user_id = str(request.user.id)

        if not description:
            return result.error("描述不能为空")
        if not model_id:
            return result.error("请选择用于生成的模型")

        def event_stream():
            for event in generate_workflow_stream(
                model_id=model_id, workspace_id=workspace_id,
                description=description, user_id=user_id,
            ):
                yield _sse(event)

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream; charset=utf-8')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response
