# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： zhipu_model_provider.py
    @date：2024/04/19 13:5
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.zhipu_model_provider.credential.image import ZhiPuImageModelCredential
from setting.models_provider.impl.zhipu_model_provider.credential.llm import ZhiPuLLMModelCredential
from setting.models_provider.impl.zhipu_model_provider.credential.tti import ZhiPuTextToImageModelCredential
from setting.models_provider.impl.zhipu_model_provider.model.image import ZhiPuImage
from setting.models_provider.impl.zhipu_model_provider.model.llm import ZhipuChatModel
from setting.models_provider.impl.zhipu_model_provider.model.tti import ZhiPuTextToImage
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

qwen_model_credential = ZhiPuLLMModelCredential()
zhipu_image_model_credential = ZhiPuImageModelCredential()
zhipu_tti_model_credential = ZhiPuTextToImageModelCredential()

model_info_list = [
    ModelInfo('glm-4', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel),
    ModelInfo('glm-4v', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel),
    ModelInfo('glm-3-turbo', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel)
]

model_info_image_list = [
    ModelInfo('glm-4v-plus', _('Have strong multi-modal understanding capabilities. Able to understand up to five images simultaneously and supports video content understanding'),
              ModelTypeConst.IMAGE, zhipu_image_model_credential,
              ZhiPuImage),
    ModelInfo('glm-4v', _('Focus on single picture understanding. Suitable for scenarios requiring efficient image analysis'),
              ModelTypeConst.IMAGE, zhipu_image_model_credential,
              ZhiPuImage),
    ModelInfo('glm-4v-flash', _('Focus on single picture understanding. Suitable for scenarios requiring efficient image analysis (free)'),
              ModelTypeConst.IMAGE, zhipu_image_model_credential,
              ZhiPuImage),
]

model_info_tti_list = [
    ModelInfo('cogview-3', _('Quickly and accurately generate images based on user text descriptions. Resolution supports 1024x1024'),
              ModelTypeConst.TTI, zhipu_tti_model_credential,
              ZhiPuTextToImage),
    ModelInfo('cogview-3-plus', _('Generate high-quality images based on user text descriptions, supporting multiple image sizes'),
              ModelTypeConst.TTI, zhipu_tti_model_credential,
              ZhiPuTextToImage),
    ModelInfo('cogview-3-flash', _('Generate high-quality images based on user text descriptions, supporting multiple image sizes (free)'),
              ModelTypeConst.TTI, zhipu_tti_model_credential,
              ZhiPuTextToImage),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(model_info_list)
    .append_default_model_info(ModelInfo('glm-4', '', ModelTypeConst.LLM, qwen_model_credential, ZhipuChatModel))
    .append_model_info_list(model_info_image_list)
    .append_default_model_info(model_info_image_list[0])
    .append_model_info_list(model_info_tti_list)
    .append_default_model_info(model_info_tti_list[0])
    .build()
)


class ZhiPuModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_zhipu_provider', name=_('zhipu AI'), icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'zhipu_model_provider', 'icon',
                         'zhipuai_icon_svg')))
