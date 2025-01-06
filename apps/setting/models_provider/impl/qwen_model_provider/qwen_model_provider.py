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
              '通义万相-文本生成图像大模型，支持中英文双语输入，支持输入参考图片进行参考内容或者参考风格迁移，重点风格包括但不限于水彩、油画、中国画、素描、扁平插画、二次元、3D卡通。',
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
        return ModelProvideInfo(provider='model_qwen_provider', name='通义千问', icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", "setting", 'models_provider', 'impl', 'qwen_model_provider', 'icon',
                         'qwen_icon_svg')))
