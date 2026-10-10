# coding=utf-8
"""
@project: MaxKB
@Author：虎虎
@file： prompt_generate_serializers.py
@desc:
"""

import json
import os

from common.config.embedding_config import ModelManage
from common.exception.app_exception import AppApiException
from common.utils.common import get_file_content, to_stream_response_simple
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from maxkb.conf import PROJECT_DIR
from models_provider.base_model_provider import ModelTypeConst
from models_provider.models import Model
from models_provider.tools import (
    get_model,
    get_model_default_params,
    get_model_instance_by_model_workspace_id,
    reset_model_params,
)
from rest_framework import serializers

SYSTEM_ROLE = get_file_content(os.path.join(PROJECT_DIR, "apps", "chat", "template", "generate_prompt_system"))


class PromptMessageSerializers(serializers.Serializer):
    role = serializers.CharField(required=True, label=_("Role"))
    content = serializers.CharField(required=True, label=_("Content"))


class PromptGenerateSerializers(serializers.Serializer):
    workspace_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Workspace ID"))
    model_id = serializers.CharField(required=False, allow_blank=True, allow_null=True, label=_("Model"))
    model_params_setting = serializers.JSONField(required=False, default=dict, label=_("Model params setting"))
    prompt = serializers.CharField(required=True, label=_("Prompt template"))
    messages = PromptMessageSerializers(many=True, required=True, label=_("Chat context"))

    def is_valid(self, *, raise_exception=False):
        super().is_valid(raise_exception=True)
        messages = self.data.get("messages") or []
        if len(messages) > 30:
            raise AppApiException(400, _("Too many messages"))
        for index in range(len(messages)):
            role = messages[index].get("role")
            if role == "ai" and index % 2 != 1:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
            if role == "user" and index % 2 != 0:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
            if role not in ["user", "ai"]:
                raise AppApiException(400, _("Authentication failed. Please verify that the parameters are correct."))
        model_id = self.data.get("model_id")
        model = QuerySet(Model).filter(id=model_id).first()
        if model is None:
            raise AppApiException(500, _("Model does not exist"))
        if model.model_type not in (ModelTypeConst.LLM.name, ModelTypeConst.IMAGE.name):
            raise AppApiException(400, _("Model does not exists or is not an LLM model"))
        # 共享/系统级模型:workspace_id 为字符串 "None",不校验传入的工作空间;否则必须属于传入的工作空间
        if model.workspace_id != "None" and self.data.get("workspace_id") != model.workspace_id:
            raise AppApiException(403, _("Model is not visible to the workspace"))
        return model

    def generate_prompt(self):
        model = self.is_valid(raise_exception=True)
        workspace_id = self.data.get("workspace_id")
        model_id = self.data.get("model_id")
        model_params_setting = self.data.get("model_params_setting") or {}
        prompt = self.data.get("prompt")
        messages = [dict(m) for m in self.data.get("messages") or []]

        message = messages[-1]["content"]
        messages[-1]["content"] = prompt.replace("{userInput}", message)

        def process():
            if model.workspace_id == "None":
                # 共享/系统级模型:不做工作空间授权,直接用模型自带认证信息实例化
                default_model_params = get_model_default_params(model)
                model_params = reset_model_params(default_model_params, **model_params_setting)
                model_instance = ModelManage.get_model(model_id, lambda _id: get_model(model, **model_params))
            else:
                model_instance = get_model_instance_by_model_workspace_id(
                    model_id=model_id, workspace_id=workspace_id, **model_params_setting
                )
            try:
                for r in model_instance.stream(
                    [
                        SystemMessage(content=SYSTEM_ROLE),
                        *[
                            HumanMessage(content=m.get("content"))
                            if m.get("role") == "user"
                            else AIMessage(content=m.get("content"))
                            for m in messages
                        ],
                    ]
                ):
                    yield "data: " + json.dumps({"content": r.content}) + "\n\n"
            except Exception as e:
                yield "data: " + json.dumps({"error": str(e)}) + "\n\n"

        return to_stream_response_simple(process())
