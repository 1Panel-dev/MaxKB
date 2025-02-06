# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： qwen_model_provider.py
    @date：2023/10/31 16:19
    @desc:
"""
import os

from common.util.file_util import get_file_content
from setting.models_provider.base_model_provider import ModelProvideInfo, ModelTypeConst, ModelInfo, IModelProvider, \
    ModelInfoManage
from setting.models_provider.impl.qwen_model_provider.credential.image import QwenVLModelCredential
from setting.models_provider.impl.qwen_model_provider.credential.llm import OpenAILLMModelCredential
from setting.models_provider.impl.qwen_model_provider.credential.tti import QwenTextToImageModelCredential
from setting.models_provider.impl.qwen_model_provider.model.image import QwenVLChatModel

from setting.models_provider.impl.qwen_model_provider.model.llm import QwenChatModel
from setting.models_provider.impl.qwen_model_provider.model.tti import QwenTextToImageModel
from smartdoc.conf import PROJECT_DIR
from django.utils.translation import gettext as _

qwen_model_credential = OpenAILLMModelCredential()
qwenvl_model_credential = QwenVLModelCredential()
qwentti_model_credential = QwenTextToImageModelCredential()

module_info_list = [
    ModelInfo('qwen-turbo', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel),
    ModelInfo('qwen-plus', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel),
    ModelInfo('qwen-max', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel)
]
module_info_vl_list = [
    ModelInfo('qwen-vl-max', '', ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
    ModelInfo('qwen-vl-max-0809', '', ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
    ModelInfo('qwen-vl-plus-0809', '', ModelTypeConst.IMAGE, qwenvl_model_credential, QwenVLChatModel),
]
module_info_tti_list = [
    ModelInfo('wanx-v1',
              _('Tongyi Wanxiang - a large image model for text generation, supports bilingual input in Chinese and English, and supports the input of reference pictures for reference content or reference style migration. Key styles include but are not limited to watercolor, oil painting, Chinese painting, sketch, flat illustration, two-dimensional, and 3D. Cartoon.'),
              ModelTypeConst.TTI, qwentti_model_credential, QwenTextToImageModel),
]

model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(module_info_list)
    .append_default_model_info(
        ModelInfo('qwen-turbo', '', ModelTypeConst.LLM, qwen_model_credential, QwenChatModel))
    .append_model_info_list(module_info_vl_list)
    .append_default_model_info(module_info_vl_list[0])
    .append_model_info_list(module_info_tti_list)
    .append_default_model_info(module_info_tti_list[0])
    .build()
)


class QwenModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_qwen_provider', name=_('Tongyi Qianwen'), icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'qwen_model_provider', 'icon',
                         'qwen_icon_svg')))
