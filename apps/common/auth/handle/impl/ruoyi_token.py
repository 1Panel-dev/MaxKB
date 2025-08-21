# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： ruoyi_token.py
    @date：2024/12/20 10:00
    @desc: Ruoyi系统Token认证处理器
"""
import requests
import json
import logging
from django.core.cache import cache
from django.db.models import QuerySet
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from common.auth.handle.auth_base_handle import AuthBaseHandle
from common.constants.authentication_type import AuthenticationType
from common.constants.permission_constants import Auth, RoleConstants, PermissionConstants
from common.exception.app_exception import AppAuthenticationFailed
from users.models import User
from common.util.common import password_encrypt


class RuoyiToken(AuthBaseHandle):
    """Ruoyi Token认证处理器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def support(self, request, token: str, get_token_details):
        """判断是否为Ruoyi Token"""
        self.logger.info(f"[RuoyiToken] ========== 开始检查是否支持当前请求 ==========")
        self.logger.info(f"[RuoyiToken] 请求路径: {request.path}")
        self.logger.info(f"[RuoyiToken] 请求方法: {request.method}")
        self.logger.info(f"[RuoyiToken] URL参数: {dict(request.GET)}")
        self.logger.info(f"[RuoyiToken] Authorization Token: {token[:20] + '...' if token and len(token) > 20 else token}")
        self.logger.info(f"[RuoyiToken] User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
        self.logger.info(f"[RuoyiToken] Referer: {request.META.get('HTTP_REFERER', 'N/A')}")

        # 方式1: 通过URL参数判断
        sparkone_token_param = request.GET.get('sparkone_token')
        if sparkone_token_param:
            self.logger.info(f"[RuoyiToken] ✅ 检测到URL参数中的sparkone_token: {sparkone_token_param[:20] + '...' if len(sparkone_token_param) > 20 else sparkone_token_param}")
            return True

        # 方式2: 通过请求头判断
        auth_type = request.META.get('HTTP_X_AUTH_TYPE')
        if auth_type == 'sparkone':
            self.logger.info(f"[RuoyiToken] ✅ 检测到请求头中的认证类型: {auth_type}")
            return True

        # 方式3: 通过token前缀判断
        if token and token.startswith('sparkone_'):
            self.logger.info(f"[RuoyiToken] ✅ 检测到token前缀匹配: sparkone_")
            return True

        # 方式4: 检查Referer
        referer = request.META.get('HTTP_REFERER', '')
        if 'ruoyi' in referer.lower() or 'sparkone' in referer.lower():
            self.logger.info(f"[RuoyiToken] ✅ 检测到Referer中包含ruoyi/sparkone: {referer}")
            return True

        self.logger.info(f"[RuoyiToken] ❌ 不支持当前请求，跳过处理")
        self.logger.info(f"[RuoyiToken] ========== 检查结束 ==========")
        return False
    
    def handle(self, request, token: str, get_token_details):
        """处理Ruoyi Token认证"""
        self.logger.info(f"[RuoyiToken] ========== 开始处理Ruoyi Token认证 ==========")
        try:
            # 获取实际的token（可能从URL参数或其他地方）
            actual_token = self._extract_token(request, token)
            self.logger.info(f"[RuoyiToken] 提取到的实际token: {actual_token[:20] + '...' if actual_token and len(actual_token) > 20 else actual_token}")

            # 1. 调用Ruoyi API验证Token
            self.logger.info(f"[RuoyiToken] 步骤1: 开始调用Ruoyi API验证Token")
            user_info = self.verify_ruoyi_token(actual_token)
            self.logger.info(f"[RuoyiToken] ✅ Token验证成功，用户信息: {user_info.get('username', 'N/A')}")

            # 2. 获取或创建本地用户
            self.logger.info(f"[RuoyiToken] 步骤2: 开始获取或创建本地用户")
            user = self.get_or_create_user(user_info)
            self.logger.info(f"[RuoyiToken] ✅ 用户处理成功: {user.username} (ID: {user.id})")

            # 3. 生成权限信息
            self.logger.info(f"[RuoyiToken] 步骤3: 开始生成权限信息")
            auth = self.create_auth(user, user_info)
            self.logger.info(f"[RuoyiToken] ✅ 权限生成成功，角色: {auth.role_list}, 权限数量: {len(auth.permission_list)}")

            self.logger.info(f"[RuoyiToken] ========== Ruoyi Token认证成功 ==========")
            return user, auth

        except Exception as e:
            self.logger.error(f"[RuoyiToken] ❌ Ruoyi认证失败: {str(e)}")
            self.logger.error(f"[RuoyiToken] ========== Ruoyi Token认证失败 ==========")
            raise AppAuthenticationFailed(1002, f'Ruoyi认证失败: {str(e)}')
    
    def _extract_token(self, request, token):
        """提取实际的token"""
        self.logger.info(f"[RuoyiToken] 开始提取实际token")

        # 优先从URL参数获取
        sparkone_token = request.GET.get('sparkone_token')
        if sparkone_token:
            self.logger.info(f"[RuoyiToken] 从URL参数获取到token: {sparkone_token[:20] + '...' if len(sparkone_token) > 20 else sparkone_token}")
            return sparkone_token

        # 从Authorization头获取
        if token and token.startswith('sparkone_'):
            extracted = token[9:]  # 去掉sparkone_前缀
            self.logger.info(f"[RuoyiToken] 从Authorization头提取token: {extracted[:20] + '...' if len(extracted) > 20 else extracted}")
            return extracted

        self.logger.info(f"[RuoyiToken] 使用原始token: {token[:20] + '...' if token and len(token) > 20 else token}")
        return token
    
    def verify_ruoyi_token(self, token: str):
        """调用Ruoyi API验证Token"""
        # 从配置获取Ruoyi系统地址
        ruoyi_base_url = getattr(settings, 'RUOYI_BASE_URL', 'http://192.168.9.88:8084')
        api_url = f"{ruoyi_base_url}/api/integration/token/verify"

        self.logger.info(f"[RuoyiToken] 准备调用Ruoyi API验证Token")
        self.logger.info(f"[RuoyiToken] API地址: {api_url}")
        self.logger.info(f"[RuoyiToken] Token: {token[:20] + '...' if token and len(token) > 20 else token}")

        try:
            # 调用Ruoyi验证接口
            response = requests.get(
                api_url,
                params={'token': token},
                timeout=10
            )

            self.logger.info(f"[RuoyiToken] API响应状态码: {response.status_code}")
            self.logger.info(f"[RuoyiToken] API响应内容: {response.text[:500] + '...' if len(response.text) > 500 else response.text}")

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    user_data = result.get('data')
                    self.logger.info(f"[RuoyiToken] ✅ Token验证成功，用户: {user_data.get('username', 'N/A')}")
                    return user_data
                else:
                    self.logger.error(f"[RuoyiToken] ❌ API返回错误: code={result.get('code')}, msg={result.get('msg')}")
                    raise Exception(f'Token验证失败: {result.get("msg", "未知错误")}')
            else:
                self.logger.error(f"[RuoyiToken] ❌ HTTP请求失败: {response.status_code}")
                raise Exception(f'Token验证失败: HTTP {response.status_code}')

        except requests.RequestException as e:
            self.logger.error(f"[RuoyiToken] ❌ 网络请求异常: {str(e)}")
            raise Exception(f'调用Ruoyi API失败: {str(e)}')
    
    def get_or_create_user(self, user_info):
        """获取或创建本地用户"""
        username = user_info.get('username')
        if not username:
            raise Exception('用户名不能为空')
            
        email = user_info.get('email', f'{username}@ruoyi.local')
        nickname = user_info.get('nickname', user_info.get('nickName', username))
        
        # 查找现有用户
        user = QuerySet(User).filter(username=username, source='RUOYI').first()
        
        if not user:
            # 创建新用户
            user = User(
                username=username,
                email=email,
                nick_name=nickname,
                source='RUOYI',  # 标记来源
                is_active=True,
                role=RoleConstants.USER.name,  # 默认角色
                password=password_encrypt('123456')  # 默认密码
            )
            user.save()
        else:
            # 更新用户信息
            user.nick_name = nickname
            user.email = email
            user.is_active = True
            user.save()
        
        return user
    
    def create_auth(self, user, user_info):
        """创建权限信息"""
        # 根据Ruoyi角色映射到本地权限
        role_permissions = user_info.get('rolePermission', [])
        menu_permissions = user_info.get('menuPermission', [])
        
        # 权限映射逻辑
        permission_list = self.map_permissions(role_permissions, menu_permissions)
        role_list = self.map_roles(role_permissions)
        
        return Auth(role_list, permission_list)
    
    def map_permissions(self, role_permissions, menu_permissions):
        """映射Ruoyi权限到本地权限"""
        permission_mapping = {
            # Ruoyi角色权限映射
            'admin': [
                'APPLICATION_READ', 'APPLICATION_CREATE', 'APPLICATION_EDIT', 'APPLICATION_DELETE',
                'KNOWLEDGE_READ', 'KNOWLEDGE_CREATE', 'KNOWLEDGE_EDIT', 'KNOWLEDGE_DELETE',
                'USER_READ', 'USER_CREATE', 'USER_EDIT', 'USER_DELETE'
            ],
            'common': [
                'APPLICATION_READ', 'KNOWLEDGE_READ'
            ],
            # 可以根据具体的菜单权限进行更细粒度的映射
            'system:user:list': ['USER_READ'],
            'system:user:add': ['USER_CREATE'],
            'system:user:edit': ['USER_EDIT'],
            'system:user:remove': ['USER_DELETE'],
        }
        
        permissions = set()
        
        # 根据角色权限映射
        for role in role_permissions:
            if role in permission_mapping:
                permissions.update(permission_mapping[role])
        
        # 根据菜单权限映射
        for menu in menu_permissions:
            if menu in permission_mapping:
                permissions.update(permission_mapping[menu])
        
        # 如果没有匹配的权限，给予基础权限
        if not permissions:
            permissions = {'APPLICATION_READ', 'KNOWLEDGE_READ'}
        
        return list(permissions)
    
    def map_roles(self, role_permissions):
        """映射Ruoyi角色到本地角色"""
        role_mapping = {
            'admin': RoleConstants.ADMIN.name,
            'common': RoleConstants.USER.name,
        }
        
        roles = []
        for role in role_permissions:
            if role in role_mapping:
                roles.append(role_mapping[role])
        
        # 如果没有匹配的角色，默认为普通用户
        if not roles:
            roles = [RoleConstants.USER.name]
        
        return roles
