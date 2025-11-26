# coding=utf-8
"""
    @project: maxkb
    @Author: Su Shi
    @file: bailing_model_provider.py
    @date: 2025/11/25 18:00
    @desc: Bailing Model Provider Implementation
"""
import os

from common.utils.common import get_file_content
from models_provider.base_model_provider import IModelProvider, ModelProvideInfo, ModelInfo, \
    ModelTypeConst, ModelInfoManage
from models_provider.impl.bailing_model_provider.credential.llm import BailingLLMModelCredential
from models_provider.impl.bailing_model_provider.model.llm import BailingChatModel
from maxkb.conf import PROJECT_DIR
from django.utils.translation import gettext_lazy as _

# LLM Model Credential
bailing_llm_model_credential = BailingLLMModelCredential()

# LLM Model Info List - Only supports Ling-1T and Ring-1T
llm_model_info_list = [
    ModelInfo('Ling-1T', _('Ling-1T is a flagship large language model of the Bailing MoE architecture series with trillion parameters, pre-trained on 20T+ high-quality corpora. This model is the latest trillion-parameter open-source model with excellent performance across various benchmark datasets, making it an ideal choice as the most user-friendly and best-experience open-source foundation model for next-generation applications.'), ModelTypeConst.LLM,
              bailing_llm_model_credential, BailingChatModel),
    ModelInfo('Ring-1T', _("Ring-1T is the world's first open-source trillion-parameter reasoning large model, and also the largest and most powerful flagship model in the Bailing MoE reasoning model Ring series. Based on the icepop method for RLVR training, this model has excellent natural language reasoning capabilities and achieves SOTA performance on benchmarks such as AIME 25, CodeForces, HMMT25, LiveCodeBench, and ARC-AGI-v1, with multiple metrics ranking first among open-source models."), ModelTypeConst.LLM,
              bailing_llm_model_credential, BailingChatModel),
]

# Model Info Manager
model_info_manage = (
    ModelInfoManage.builder()
    .append_model_info_list(llm_model_info_list)
    .append_default_model_info(llm_model_info_list[0])  # Default LLM Model
    .build()
)


class BailingModelProvider(IModelProvider):

    def get_model_info_manage(self):
        return model_info_manage

    def get_model_provide_info(self):
        return ModelProvideInfo(provider='model_bailing_provider', name=_('Bailing'), icon=get_file_content(
            os.path.join(PROJECT_DIR, "apps", 'models_provider', 'impl', 'bailing_model_provider', 'icon',
                         'bailing_icon_svg')))

