# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： application_access_token_cache.py
    @date：2024/7/25 11:34
    @desc:
"""
from django.core.cache import cache
from django.db.models import QuerySet

from application.models.api_key_model import ApplicationAccessToken
from common.constants.cache_code_constants import CacheCodeConstants
from common.util.cache_util import get_cache


@get_cache(cache_key=lambda access_token, use_get_data: access_token,
           use_get_data=lambda access_token, use_get_data: use_get_data,
           version=CacheCodeConstants.APPLICATION_ACCESS_TOKEN_CACHE.value)
def get_application_access_token(access_token, use_get_data):
    application_access_token = QuerySet(ApplicationAccessToken).filter(access_token=access_token).first()
    if application_access_token is None:
        return None
    return {'white_active': application_access_token.white_active,
            'white_list': application_access_token.white_list,
            'application_icon': application_access_token.application.icon,
            'application_name': application_access_token.application.name}


def del_application_access_token(access_token):
    cache.delete(access_token, version=CacheCodeConstants.APPLICATION_ACCESS_TOKEN_CACHE.value)
