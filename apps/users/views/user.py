# coding=utf-8
"""
    @project: qabot
    @Author：虎
    @file： user.py
    @date：2023/9/4 10:57
    @desc:
"""
from django.core import cache
from django.db.models import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.views import Request

from common.auth.authenticate import TokenAuth
from common.auth.authentication import has_permissions
from common.constants.permission_constants import PermissionConstants, CompareConstants
from common.response import result
from smartdoc.settings import JWT_AUTH
from users.models.user import User as UserModel
from users.serializers.user_serializers import RegisterSerializer, LoginSerializer, CheckCodeSerializer, \
    RePasswordSerializer, \
    SendEmailSerializer, UserProfile

user_cache = cache.caches['user_cache']
token_cache = cache.caches['token_cache']


class User(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="获取当前用户信息",
                         operation_id="获取当前用户信息",
                         responses=result.get_api_response(UserProfile.get_response_body_api()))
    @has_permissions(PermissionConstants.USER_READ, compare=CompareConstants.AND)
    def get(self, request: Request):
        return result.success(UserProfile.get_user_profile(request.user))


class ResetCurrentUserPasswordView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="修改当前用户密码",
                         operation_id="修改当前用户密码",
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             required=['email', 'code', "password", 're_password'],
                             properties={
                                 'code': openapi.Schema(type=openapi.TYPE_STRING, title="验证码", description="验证码"),
                                 'password': openapi.Schema(type=openapi.TYPE_STRING, title="密码", description="密码"),
                                 're_password': openapi.Schema(type=openapi.TYPE_STRING, title="密码",
                                                               description="密码")
                             }
                         ),
                         responses=RePasswordSerializer().get_response_body_api())
    def post(self, request: Request):
        data = {'email': request.user.email}
        data.update(request.data)
        serializer_obj = RePasswordSerializer(data=data)
        if serializer_obj.reset_password():
            token_cache.delete(request.META.get('HTTP_AUTHORIZATION', None
                                                ))
            return result.success(True)
        return result.error("修改密码失败")


class SendEmailToCurrentUserView(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary="发送邮件到当前用户",
                         operation_id="发送邮件到当前用户",
                         responses=SendEmailSerializer().get_response_body_api())
    def post(self, request: Request):
        serializer_obj = SendEmailSerializer(data={'email': request.user.email, 'type': "reset_password"})
        if serializer_obj.is_valid(raise_exception=True):
            return result.success(serializer_obj.send())


class Logout(APIView):
    authentication_classes = [TokenAuth]

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary="登出",
                         operation_id="登出",
                         responses=SendEmailSerializer().get_response_body_api())
    def post(self, request: Request):
        token_cache.delete(request.META.get('HTTP_AUTHORIZATION', None
                                            ))
        return result.success(True)


class Login(APIView):

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="登录",
                         operation_id="登录",
                         request_body=LoginSerializer().get_request_body_api(),
                         responses=LoginSerializer().get_response_body_api())
    def post(self, request: Request):
        login_request = LoginSerializer(data=request.data)
        # 校验请求参数
        user = login_request.is_valid(raise_exception=True)
        token = login_request.get_user_token()
        token_cache.set(token, user, timeout=JWT_AUTH['JWT_EXPIRATION_DELTA'])
        return result.success(token)


class Register(APIView):

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary="用户注册",
                         operation_id="用户注册",
                         request_body=RegisterSerializer().get_request_body_api(),
                         responses=RegisterSerializer().get_response_body_api())
    def post(self, request: Request):
        serializer_obj = RegisterSerializer(data=request.data)
        if serializer_obj.is_valid(raise_exception=True):
            serializer_obj.save()
            return result.success("注册成功")


class RePasswordView(APIView):

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary="修改密码",
                         operation_id="修改密码",
                         request_body=RePasswordSerializer().get_request_body_api(),
                         responses=RePasswordSerializer().get_response_body_api())
    def post(self, request: Request):
        serializer_obj = RePasswordSerializer(data=request.data)
        return result.success(serializer_obj.reset_password())


class CheckCode(APIView):

    @action(methods=['POST'], detail=False)
    @permission_classes((AllowAny,))
    @swagger_auto_schema(operation_summary="校验验证码是否正确",
                         operation_id="校验验证码是否正确",
                         request_body=CheckCodeSerializer().get_request_body_api(),
                         responses=CheckCodeSerializer().get_response_body_api())
    def post(self, request: Request):
        return result.success(CheckCodeSerializer(data=request.data).is_valid(raise_exception=True))


class SendEmail(APIView):

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="发送邮件",
                         operation_id="发送邮件",
                         request_body=SendEmailSerializer().get_request_body_api(),
                         responses=SendEmailSerializer().get_response_body_api())
    def post(self, request: Request):
        serializer_obj = SendEmailSerializer(data=request.data)
        if serializer_obj.is_valid(raise_exception=True):
            return result.success(serializer_obj.send())
