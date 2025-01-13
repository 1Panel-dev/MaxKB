from typing import List

from django.http import JsonResponse
from drf_yasg import openapi
from rest_framework import status
from django.utils.translation import gettext_lazy as _


class Page(dict):
    """
    分页对象
    """

    def __init__(self, total: int, records: List, current_page: int, page_size: int, **kwargs):
        super().__init__(**{'total': total, 'records': records, 'current': current_page, 'size': page_size})


class Result(JsonResponse):
    charset = 'utf-8'
    """
     接口统一返回对象
    """

    def __init__(self, code=200, message=_('Success'), data=None, response_status=status.HTTP_200_OK, **kwargs):
        back_info_dict = {"code": code, "message": message, 'data': data}
        super().__init__(data=back_info_dict, status=response_status, **kwargs)


def get_page_request_params(other_request_params=None):
    if other_request_params is None:
        other_request_params = []
    current_page = openapi.Parameter(name='current_page',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_INTEGER,
                                     required=True,
                                     description=_('current page'))

    page_size = openapi.Parameter(name='page_size',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_INTEGER,
                                  required=True,
                                  description=_('page size'))
    result = [current_page, page_size]
    for other_request_param in other_request_params:
        result.append(other_request_param)
    return result


def get_page_api_response(response_data_schema: openapi.Schema):
    """
        获取统一返回 响应Api
    """
    return openapi.Responses(responses={200: openapi.Response(description=_('response parameters'),
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title=_('response code'),
                                                                          default=200,
                                                                          description=_('success:200 fail:other')),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title=_('prompt'),
                                                                          default=_('success'),
                                                                          description=_('error prompt')),
                                                                      "data": openapi.Schema(
                                                                          type=openapi.TYPE_OBJECT,
                                                                          properties={
                                                                              'total': openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title=_('total number of data'),
                                                                                  default=1,
                                                                                  description=_('total number of data')),
                                                                              "records": openapi.Schema(
                                                                                  type=openapi.TYPE_ARRAY,
                                                                                  items=response_data_schema),
                                                                              "current": openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title=_('current page'),
                                                                                  default=1,
                                                                                  description=_('current page')),
                                                                              "size": openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title=_('page size'),
                                                                                  default=10,
                                                                                  description=_('page size'))

                                                                          }
                                                                      )

                                                                  }
                                                              ),
                                                              )})


def get_api_response(response_data_schema: openapi.Schema):
    """
    获取统一返回 响应Api
    """
    return openapi.Responses(responses={200: openapi.Response(description=_('response parameters'),
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title=_('response code'),
                                                                          default=200,
                                                                          description=_('success:200 fail:other')),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title=_('prompt'),
                                                                          default=_('success'),
                                                                          description=_('error prompt')),
                                                                      "data": response_data_schema

                                                                  }
                                                              ),
                                                              )})


def get_default_response():
    return get_api_response(openapi.Schema(type=openapi.TYPE_BOOLEAN))


def get_api_array_response(response_data_schema: openapi.Schema):
    """
    获取统一返回 响应Api
    """
    return openapi.Responses(responses={200: openapi.Response(description=_('response parameters'),
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title=_('response code'),
                                                                          default=200,
                                                                          description=_('success:200 fail:other')),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title=_('prompt'),
                                                                          default=_('success'),
                                                                          description=_('error prompt')),
                                                                      "data": openapi.Schema(type=openapi.TYPE_ARRAY,
                                                                                             items=response_data_schema)

                                                                  }
                                                              ),
                                                              )})


def success(data, **kwargs):
    """
    获取一个成功的响应对象
    :param data: 接口响应数据
    :return: 请求响应对象
    """
    return Result(data=data, **kwargs)


def error(message, **kwargs):
    """
    获取一个失败的响应对象
    :param message: 错误提示
    :return: 接口响应对象
    """
    return Result(code=500, message=message, **kwargs)
