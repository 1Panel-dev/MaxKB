# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： common.py
    @date：2025/3/25 16:26
    @desc:
"""
from django.db.models import QuerySet

from common.util.common import encryption
from setting.models import Model
from users.models import User


def get_model_operation_object(model_id):
    model_model = QuerySet(model=Model).filter(id=model_id).first()
    if model_model is not None:
        return {
            "name": model_model.name
        }
    return {}


def get_member_operation_object(member_id):
    user_model = QuerySet(model=User).filter(id=member_id).first()
    if user_model is not None:
        return {
            "name": user_model.username
        }
    return {}


def get_member_operation_object_batch(member_id_list):
    user_model_list = QuerySet(model=User).filter(id__in=member_id_list)
    if user_model_list is not None:
        return {
            "name": f'[{",".join([user.username for user in user_model_list])}]',
            "user_list": [{'name': user.username} for user in user_model_list]
        }
    return {}


def encryption_str(_value):
    if isinstance(_value, str):
        return encryption(_value)
    return _value


def encryption_credential(credential):
    if isinstance(credential, dict):
        return {key: encryption_str(credential.get(key)) for key in credential}
    return credential


def get_edit_model_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    credential = body.get('credential', {})
    credential_encryption_ed = encryption_credential(credential)
    return {
        'path': path,
        'body': {**body, 'credential': credential_encryption_ed},
        'query': query
    }


def get_email_details(request):
    path = request.path
    body = request.data
    query = request.query_params
    email_host_password = body.get('email_host_password', '')
    return {
        'path': path,
        'body': {**body, 'email_host_password': encryption_str(email_host_password)},
        'query': query
    }
