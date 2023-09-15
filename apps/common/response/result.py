from django.http import JsonResponse
from drf_yasg import openapi
from rest_framework import status


class Result(JsonResponse):
    """
     接口统一返回对象
    """

    def __init__(self, code=200, message="成功", data=None, response_status=status.HTTP_200_OK, **kwargs):
        back_info_dict = {"code": code, "message": message, 'data': data}
        super().__init__(data=back_info_dict, status=response_status)


def get_api_response(response_data_schema: openapi.Schema, data_examples):
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
                                                              examples={'code': 200,
                                                                        'data': data_examples,
                                                                        'message': "成功"})})


def success(data):
    """
    获取一个成功的响应对象
    :param data: 接口响应数据
    :return: 请求响应对象
    """
    return Result(data=data)


def error(message):
    """
    获取一个失败的响应对象
    :param message: 错误提示
    :return: 接口响应对象
    """
    return Result(code=500, message=message)
