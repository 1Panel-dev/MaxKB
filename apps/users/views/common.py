# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： common.py
    @date：2025/3/25 16:46
    @desc:
"""
from common.util.common import encryption
from users.models import User
from django.db.models import QuerySet


def get_user_operation_object(user_id):
    user_model = QuerySet(model=User).filter(id=user_id).first()
    if user_model is not None:
        return {
            "name": user_model.username
        }
    return {}


def get_re_password_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    return {
        'path': path,
        'body': {**body, 'password': encryption(body.get('password', '')),
                 're_password': encryption(body.get('re_password', ''))},
        'query': query
    }
