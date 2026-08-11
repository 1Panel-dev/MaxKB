from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework.request import Request
from rest_framework.views import APIView

from application.models import Application
from application.models.application_access_token import ApplicationAccessToken
from common import result
from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import RoleConstants
from role.api.resource_manage import SystemApplicationAPI, SystemApplicationAccessTokenAPI


class SystemApplicationView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get system application list by page"),
        summary=_("Get system application list by page"),
        operation_id=_("Get system application list by page"),
        parameters=SystemApplicationAPI.get_parameters(),
        responses=SystemApplicationAPI.get_page_response(),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, current_page: int, page_size: int):
        from application.serializers.application import Query

        qs = Application.objects.all().order_by("-create_time")
        name = request.query_params.get("name")
        create_user = request.query_params.get("create_user")
        app_type = request.query_params.get("type")
        if name:
            qs = qs.filter(name__icontains=name)
        if create_user:
            qs = qs.filter(user_id=create_user)
        if app_type:
            qs = qs.filter(type=app_type)
        total = qs.count()
        start = (current_page - 1) * page_size
        page_qs = qs[start : start + page_size]
        records = []
        for app in page_qs:
            records.append(
                {
                    "id": str(app.id),
                    "name": app.name,
                    "type": app.type,
                    "is_publish": app.is_publish,
                    "icon": app.icon,
                    "nick_name": app.user.nick_name if app.user else "",
                    "workspace_id": app.workspace_id,
                    "create_time": app.create_time.isoformat() if app.create_time else None,
                    "update_time": app.update_time.isoformat() if app.update_time else None,
                }
            )
        return result.success({"total": total, "records": records})


class SystemApplicationDeleteView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["DELETE"],
        description=_("Delete application from system"),
        summary=_("Delete application from system"),
        operation_id=_("Delete application from system"),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def delete(self, request: Request, application_id: str):
        from application.serializers.application import ApplicationOperateSerializer

        app = Application.objects.filter(id=application_id).first()
        if not app:
            return result.error("应用不存在")
        ApplicationOperateSerializer(
            data={
                "application_id": application_id,
                "workspace_id": app.workspace_id,
                "user_id": request.user.id,
            }
        ).delete()
        return result.success("ok")


class SystemApplicationAccessTokenView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get application access token"),
        summary=_("Get application access token"),
        operation_id=_("Get application access token"),
        parameters=SystemApplicationAccessTokenAPI.get_parameters(),
        responses=SystemApplicationAccessTokenAPI.get_response(),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, application_id: str):
        token = ApplicationAccessToken.objects.filter(application_id=application_id).first()
        if not token:
            return result.success(None)
        return result.success(
            {
                "application_id": str(token.application_id),
                "access_token": token.access_token,
                "is_active": token.is_active,
                "access_num": token.access_num,
                "white_active": token.white_active,
                "white_list": token.white_list,
                "show_source": token.show_source,
                "show_exec": token.show_exec,
                "authentication": token.authentication,
                "authentication_value": token.authentication_value,
                "language": token.language,
            }
        )


class SystemApplicationExportView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Export application"),
        summary=_("Export application"),
        operation_id=_("Export application from system"),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, application_id: str):
        from application.serializers.application import ApplicationOperateSerializer

        app = Application.objects.filter(id=application_id).first()
        if not app:
            return result.error("应用不存在")
        return ApplicationOperateSerializer(
            data={
                "application_id": application_id,
                "workspace_id": app.workspace_id,
                "user_id": request.user.id,
            }
        ).export()


from knowledge.models import Knowledge
from tools.models import Tool
from models_provider.models import Model as ModelProviderModel
from role.api.resource_manage import (
    SystemApplicationAPI,
    SystemApplicationAccessTokenAPI,
    SystemKnowledgeAPI,
    SystemToolAPI,
    SystemModelAPI,
)


class SystemKnowledgeView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get system knowledge list by page"),
        summary=_("Get system knowledge list by page"),
        operation_id=_("Get system knowledge list by page"),
        parameters=SystemKnowledgeAPI.get_parameters(),
        responses=SystemKnowledgeAPI.get_page_response(),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, current_page: int, page_size: int):
        qs = Knowledge.objects.all().order_by("-create_time")
        name = request.query_params.get("name")
        create_user = request.query_params.get("create_user")
        k_type = request.query_params.get("type")
        if name:
            qs = qs.filter(name__icontains=name)
        if create_user:
            qs = qs.filter(user_id=create_user)
        if k_type is not None:
            qs = qs.filter(type=int(k_type))
        total = qs.count()
        start = (current_page - 1) * page_size
        page_qs = qs[start : start + page_size]
        records = []
        for obj in page_qs:
            records.append(
                {
                    "id": str(obj.id),
                    "name": obj.name,
                    "type": obj.type,
                    "nick_name": obj.user.nick_name if obj.user else "",
                    "workspace_id": obj.workspace_id,
                    "create_time": obj.create_time.isoformat() if obj.create_time else None,
                    "update_time": obj.update_time.isoformat() if obj.update_time else None,
                }
            )
        return result.success({"total": total, "records": records})


class SystemKnowledgeDeleteView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["DELETE"],
        description=_("Delete knowledge from system"),
        summary=_("Delete knowledge from system"),
        operation_id=_("Delete knowledge from system"),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def delete(self, request: Request, knowledge_id: str):
        obj = Knowledge.objects.filter(id=knowledge_id).first()
        if not obj:
            return result.error("知识库不存在")
        obj.delete()
        return result.success("ok")


class SystemToolView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get system tool list by page"),
        summary=_("Get system tool list by page"),
        operation_id=_("Get system tool list by page"),
        parameters=SystemToolAPI.get_parameters(),
        responses=SystemToolAPI.get_page_response(),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, current_page: int, page_size: int):
        qs = Tool.objects.all().order_by("-create_time")
        name = request.query_params.get("name")
        create_user = request.query_params.get("create_user")
        tool_type = request.query_params.get("tool_type")
        source = request.query_params.get("source")
        if name:
            qs = qs.filter(name__icontains=name)
        if create_user:
            qs = qs.filter(user_id=create_user)
        if tool_type:
            qs = qs.filter(tool_type=tool_type)
        if source == "TOOL_STORE":
            qs = qs.filter(template_id__isnull=False)
        elif source == "CUSTOM":
            qs = qs.filter(template_id__isnull=True)
        total = qs.count()
        start = (current_page - 1) * page_size
        page_qs = qs[start : start + page_size]
        records = []
        for obj in page_qs:
            records.append(
                {
                    "id": str(obj.id),
                    "name": obj.name,
                    "tool_type": obj.tool_type,
                    "is_active": obj.is_active,
                    "template_id": obj.template_id,
                    "nick_name": obj.user.nick_name if obj.user else "",
                    "workspace_id": obj.workspace_id,
                    "create_time": obj.create_time.isoformat() if obj.create_time else None,
                    "update_time": obj.update_time.isoformat() if obj.update_time else None,
                }
            )
        return result.success({"total": total, "records": records})


class SystemToolDeleteView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["DELETE"],
        description=_("Delete tool from system"),
        summary=_("Delete tool from system"),
        operation_id=_("Delete tool from system"),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def delete(self, request: Request, tool_id: str):
        obj = Tool.objects.filter(id=tool_id).first()
        if not obj:
            return result.error("工具不存在")
        obj.delete()
        return result.success("ok")


class SystemModelView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["GET"],
        description=_("Get system model list by page"),
        summary=_("Get system model list by page"),
        operation_id=_("Get system model list by page"),
        parameters=SystemModelAPI.get_parameters(),
        responses=SystemModelAPI.get_page_response(),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def get(self, request: Request, current_page: int, page_size: int):
        qs = ModelProviderModel.objects.all().order_by("-create_time")
        name = request.query_params.get("name")
        create_user = request.query_params.get("create_user")
        model_type = request.query_params.get("model_type")
        if name:
            qs = qs.filter(name__icontains=name)
        if create_user:
            qs = qs.filter(user_id=create_user)
        if model_type:
            qs = qs.filter(model_type=model_type)
        total = qs.count()
        start = (current_page - 1) * page_size
        page_qs = qs[start : start + page_size]
        records = []
        for obj in page_qs:
            records.append(
                {
                    "id": str(obj.id),
                    "name": obj.name,
                    "provider": obj.provider,
                    "model_type": obj.model_type,
                    "model_name": obj.model_name,
                    "nick_name": obj.user.nick_name if obj.user else "",
                    "workspace_id": obj.workspace_id,
                    "create_time": obj.create_time.isoformat() if obj.create_time else None,
                    "update_time": obj.update_time.isoformat() if obj.update_time else None,
                }
            )
        return result.success({"total": total, "records": records})


class SystemModelDeleteView(APIView):
    authentication_classes = [TokenAuth]

    @extend_schema(
        methods=["DELETE"],
        description=_("Delete model from system"),
        summary=_("Delete model from system"),
        operation_id=_("Delete model from system"),
        tags=[_("System Resource")],
    )
    @has_permissions(RoleConstants.ADMIN)
    def delete(self, request: Request, model_id: str):
        obj = ModelProviderModel.objects.filter(id=model_id).first()
        if not obj:
            return result.error("模型不存在")
        obj.delete()
        return result.success("ok")
