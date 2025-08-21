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
    
    def support(self, request, token: str, get_token_details):
        """判断是否为Ruoyi Token"""
        # 方式1: 通过URL参数判断
        if request.GET.get('sparkone_token'):
            return True
            
        # 方式2: 通过请求头判断
        if request.META.get('HTTP_X_AUTH_TYPE') == 'ruoyi':
            return True
            
        # 方式3: 通过token前缀判断（如果Ruoyi有特定前缀）
        if token and token.startswith('sparkone_'):
            return True
            
        # 方式4: 检查是否在iframe环境中且有ruoyi标识
        referer = request.META.get('HTTP_REFERER', '')
        if 'ruoyi' in referer.lower():
            return True
            
        return False
    
    def handle(self, request, token: str, get_token_details):
        """处理Ruoyi Token认证"""
        try:
            # 获取实际的token（可能从URL参数或其他地方）
            actual_token = self._extract_token(request, token)
            
            # 1. 调用Ruoyi API验证Token
            user_info = self.verify_ruoyi_token(actual_token)
            
            # 2. 获取或创建本地用户
            user = self.get_or_create_user(user_info)
            
            # 3. 生成权限信息
            auth = self.create_auth(user, user_info)
            
            return user, auth
            
        except Exception as e:
            raise AppAuthenticationFailed(1002, f'Ruoyi认证失败: {str(e)}')
    
    def _extract_token(self, request, token):
        """提取实际的token"""
        # 优先从URL参数获取
        ruoyi_token = request.GET.get('sparkone_')
        if ruoyi_token:
            return ruoyi_token
            
        # 从Authorization头获取
        if token and token.startswith('sparkone_'):
            return token[6:]  # 去掉ruoyi_前缀
            
        return token
    
    def verify_ruoyi_token(self, token: str):
        """调用Ruoyi API验证Token"""
        # 从配置获取Ruoyi系统地址
        ruoyi_base_url = getattr(settings, 'RUOYI_BASE_URL', 'http://192.168.9.88:8084')
        
        try:
            # 调用Ruoyi验证接口
            response = requests.get(
                f"{ruoyi_base_url}/api/integration/token/verify",
                params={'token': token},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return result.get('data')
            
            raise Exception(f'Token验证失败: {response.text}')
            
        except requests.RequestException as e:
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
