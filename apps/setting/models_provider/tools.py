# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： tools.py
    @date：2024/7/22 11:18
    @desc:
"""
from django.db.models import QuerySet

from common.config.embedding_config import ModelManage
from setting.models import Model
from setting.models_provider import get_model


def get_model_by_id(_id, user_id):
    model = QuerySet(Model).filter(id=_id).first()
    if model is None:
        raise Exception("模型不存在")
    if model.permission_type == 'PRIVATE' and str(model.user_id) != str(user_id):
        raise Exception(f"无权限使用此模型:{model.name}")
    return model


def get_model_instance_by_model_user_id(model_id, user_id):
    """
    获取模型实例,根据模型相关数据
    @param model_id:  模型id
    @param user_id:   用户id
    @return:          模型实例
    """
    model = get_model_by_id(model_id, user_id)
    return ModelManage.get_model(model_id, lambda _id: get_model(model))
