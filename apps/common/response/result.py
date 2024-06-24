from typing import List

from django.http import JsonResponse
from drf_yasg import openapi
from rest_framework import status


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

    def __init__(self, code=200, message="成功", data=None, response_status=status.HTTP_200_OK, **kwargs):
        back_info_dict = {"code": code, "message": message, 'data': data}
        super().__init__(data=back_info_dict, status=response_status, **kwargs)


def get_page_request_params(other_request_params=None):
    if other_request_params is None:
        other_request_params = []
    current_page = openapi.Parameter(name='current_page',
                                     in_=openapi.IN_PATH,
                                     type=openapi.TYPE_INTEGER,
                                     required=True,
                                     description='当前页')

    page_size = openapi.Parameter(name='page_size',
                                  in_=openapi.IN_PATH,
                                  type=openapi.TYPE_INTEGER,
                                  required=True,
                                  description='每页大小')
    result = [current_page, page_size]
    for other_request_param in other_request_params:
        result.append(other_request_param)
    return result


def get_page_api_response(response_data_schema: openapi.Schema):
    """
        获取统一返回 响应Api
    """
    return openapi.Responses(responses={200: openapi.Response(description="响应参数",
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title="响应码",
                                                                          default=200,
                                                                          description="成功:200 失败:其他"),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title="提示",
                                                                          default='成功',
                                                                          description="错误提示"),
                                                                      "data": openapi.Schema(
                                                                          type=openapi.TYPE_OBJECT,
                                                                          properties={
                                                                              'total': openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title="总条数",
                                                                                  default=1,
                                                                                  description="数据总条数"),
                                                                              "records": openapi.Schema(
                                                                                  type=openapi.TYPE_ARRAY,
                                                                                  items=response_data_schema),
                                                                              "current": openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title="当前页",
                                                                                  default=1,
                                                                                  description="当前页"),
                                                                              "size": openapi.Schema(
                                                                                  type=openapi.TYPE_INTEGER,
                                                                                  title="每页大小",
                                                                                  default=10,
                                                                                  description="每页大小")

                                                                          }
                                                                      )

                                                                  }
                                                              ),
                                                              )})


def get_api_response(response_data_schema: openapi.Schema):
    """
    获取统一返回 响应Api
    """
    return openapi.Responses(responses={200: openapi.Response(description="响应参数",
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title="响应码",
                                                                          default=200,
                                                                          description="成功:200 失败:其他"),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title="提示",
                                                                          default='成功',
                                                                          description="错误提示"),
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
    return openapi.Responses(responses={200: openapi.Response(description="响应参数",
                                                              schema=openapi.Schema(
                                                                  type=openapi.TYPE_OBJECT,
                                                                  properties={
                                                                      'code': openapi.Schema(
                                                                          type=openapi.TYPE_INTEGER,
                                                                          title="响应码",
                                                                          default=200,
                                                                          description="成功:200 失败:其他"),
                                                                      "message": openapi.Schema(
                                                                          type=openapi.TYPE_STRING,
                                                                          title="提示",
                                                                          default='成功',
                                                                          description="错误提示"),
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


def error(message):
    """
    获取一个失败的响应对象
    :param message: 错误提示
    :return: 接口响应对象
    """
    return Result(code=500, message=message)
