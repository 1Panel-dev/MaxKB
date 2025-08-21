# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： ruoyi_login.py
    @date：2024/12/20 10:30
    @desc: Ruoyi系统登录API
"""
import uuid
from django.core.cache import cache
from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from common.auth.handle.impl.ruoyi_token import RuoyiToken
from common.exception.app_exception import AppApiException
from common.response import result
from common.util.common import query_params_to_single_dict
from users.models import User
from users.serializers.common import UserSerializer
from users.serializers.login import LoginSerializer


class RuoyiLoginApi(APIView):
    authentication_classes = []

    @action(methods=['POST'], detail=False)
    @swagger_auto_schema(operation_summary="Ruoyi Token登录",
                         operation_id="Ruoyi Token登录",
                         request_body=LoginSerializer,
                         responses=result.get_api_response(UserSerializer),
                         tags=["用户管理"])
    def ruoyi_login(self, request: Request):
        """
        Ruoyi Token登录接口
        """
        try:
            # 获取token
            token = request.data.get('token') or request.GET.get('sparkone_token')
            if not token:
                return result.error(message="Token不能为空")

            # 使用RuoyiToken处理器验证token
            ruoyi_handler = RuoyiToken()
            
            # 验证token并获取用户信息
            user_info = ruoyi_handler.verify_ruoyi_token(token)
            
            # 获取或创建用户
            user = ruoyi_handler.get_or_create_user(user_info)
            
            # 生成MaxKB内部token
            maxkb_token = self.generate_maxkb_token(user, user_info)
            
            # 返回用户信息和token
            user_data = UserSerializer(user, many=False).data
            user_data['token'] = maxkb_token
            
            return result.success(user_data)
            
        except Exception as e:
            return result.error(message=f"Ruoyi登录失败: {str(e)}")

    def generate_maxkb_token(self, user, user_info):
        """生成MaxKB内部token"""
        # 生成唯一token
        token = str(uuid.uuid4())
        
        # 构建认证详情
        auth_details = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nick_name': user.nick_name,
            'role': user.role,
            'source': 'RUOYI',
            'ruoyi_user_info': user_info  # 保存Ruoyi用户信息
        }
        
        # 缓存token信息（24小时有效）
        cache_key = f"user_token_{token}"
        cache.set(
            cache_key,
            {
                'password': user.password,
                'auth_details': auth_details
            },
            timeout=24 * 60 * 60  # 24小时
        )
        
        return token

    @action(methods=['GET'], detail=False)
    @swagger_auto_schema(operation_summary="检查Ruoyi Token状态",
                         operation_id="检查Ruoyi Token状态",
                         responses=result.get_api_response(UserSerializer),
                         tags=["用户管理"])
    def check_ruoyi_status(self, request: Request):
        """
        检查Ruoyi Token状态
        """
        try:
            token = request.GET.get('sparkone_token')
            if not token:
                return result.error(message="Token不能为空")

            # 验证token
            ruoyi_handler = RuoyiToken()
            user_info = ruoyi_handler.verify_ruoyi_token(token)
            
            return result.success({
                'valid': True,
                'username': user_info.get('username'),
                'nickname': user_info.get('nickname', user_info.get('nickName')),
                'roles': user_info.get('rolePermission', [])
            })
            
        except Exception as e:
            return result.success({
                'valid': False,
                'error': str(e)
            })
