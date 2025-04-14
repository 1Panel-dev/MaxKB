# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎
    @file： ApiMixin.py
    @date：2025/4/14 18:03
    @desc:
"""


class APIMixin:
    @staticmethod
    def get_request():
        return None

    @staticmethod
    def get_response():
        return None

    @staticmethod
    def get_parameters():
        """
         return OpenApiParameter(
            # 参数的名称是done
            name="done",
            # 对参数的备注
            description="是否完成",
            # 指定参数的类型
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            # 指定必须给
            required=True,
            # 指定枚举项
            enum=[True, False],
        )

        """
        return None
