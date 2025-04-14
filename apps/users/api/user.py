# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： user.py
    @date：2025/4/14 19:23
    @desc:
"""
from common.mixins.api_mixin import APIMixin
from common.result import ResultSerializer
from users.serializers.user import UserProfileResponse


class ApiUserProfileResponse(ResultSerializer):
    def get_data(self):
        return UserProfileResponse()


class UserProfileAPI(APIMixin):

    @staticmethod
    def get_response():
        return ApiUserProfileResponse
