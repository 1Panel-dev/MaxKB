# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： common.py
    @date：2025/3/25 16:56
    @desc:
"""

from django.db.models import QuerySet

from application.models import Application


def get_application_operation_object(application_id):
    application_model = QuerySet(model=Application).filter(id=application_id).first()
    if application_model is not None:
        return {
            "name": application_model.name
        }
    return {}
