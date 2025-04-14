# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:18
    @desc:
"""
from rest_framework import serializers

from users.models import User


class UserProfileResponse(serializers.ModelSerializer):
    is_edit_password = serializers.BooleanField(required=True, label="是否修改密码")
    permissions = serializers.ListField(required=True, label="权限")

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'permissions', 'language', 'is_edit_password']


class UserProfileSerializer(serializers.Serializer):
    @staticmethod
    def profile(user: User):
        """
        获取用户详情
        :param user: 用户对象
        :return:
        """
        return {'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'permissions': [str(p) for p in []],
                'is_edit_password': user.password == 'd880e722c47a34d8e9fce789fc62389d' if user.role == 'ADMIN' else False,
                'language': user.language}
