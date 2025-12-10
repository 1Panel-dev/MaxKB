# coding=utf-8
"""
讯飞超拟人语音合成 (Super Humanoid TTS) Credential
"""
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode


class XunFeiSuperHumanoidTTSModelParams(BaseForm):
    """超拟人语音合成参数"""
    vcn = forms.SingleSelect(
        TooltipLabel(_('Speaker'), _('Speaker selection for super-humanoid TTS service')),
        required=True, default_value='x5_lingxiaoxuan_flow',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': _('Super-humanoid: Lingxiaoxuan Flow'), 'value': 'x5_lingxiaoxuan_flow'},
            {'text': _('Super-humanoid: Lingyuyan Flow'), 'value': 'x5_lingyuyan_flow'},
            {'text': _('Super-humanoid: Lingfeiyi Flow'), 'value': 'x5_lingfeiyi_flow'},
            {'text': _('Super-humanoid: Lingxiaoyue Flow'), 'value': 'x5_lingxiaoyue_flow'},
            {'text': _('Super-humanoid: Sun Dasheng Flow'), 'value': 'x5_sundasheng_flow'},
            {'text': _('Super-humanoid: Lingyuzhao Flow'), 'value': 'x5_lingyuzhao_flow'},
            {'text': _('Super-humanoid: Lingxiaotang Flow'), 'value': 'x5_lingxiaotang_flow'},
            {'text': _('Super-humanoid: Lingxiaorong Flow'), 'value': 'x5_lingxiaorong_flow'},
            {'text': _('Super-humanoid: Xinyun Flow'), 'value': 'x5_xinyun_flow'},
            {'text': _('Super-humanoid: Grant (EN)'), 'value': 'x5_EnUs_Grant_flow'},
            {'text': _('Super-humanoid: Lila (EN)'), 'value': 'x5_EnUs_Lila_flow'},
            {'text': _('Super-humanoid: Lingwanwan Pro'), 'value': 'x6_lingwanwan_pro'},
            {'text': _('Super-humanoid: Yiyi Pro'), 'value': 'x6_yiyi_pro'},
            {'text': _('Super-humanoid: Huifangnv Pro'), 'value': 'x6_huifangnv_pro'},
            {'text': _('Super-humanoid: Lingxiaoying Pro'), 'value': 'x6_lingxiaoying_pro'},
            {'text': _('Super-humanoid: Lingfeibo Pro'), 'value': 'x6_lingfeibo_pro'},
            {'text': _('Super-humanoid: Lingyuyan Pro'), 'value': 'x6_lingyuyan_pro'},
        ])

    speed = forms.SliderField(
        TooltipLabel(_('speaking speed'), _('Speech speed, optional value: [0-100], default is 50')),
        required=True, default_value=50,
        _min=1,
        _max=100,
        _step=5,
        precision=1)


class XunFeiSuperHumanoidTTSModelCredential(BaseForm, BaseModelCredential):
    """讯飞超拟人语音合成 Credential"""
    spark_api_url = forms.TextInputField('API URL', required=True,
                                         default_value='wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6')
    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        required_keys = ['spark_api_url', 'spark_app_id', 'spark_api_key', 'spark_api_secret']

        for key in required_keys:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key} is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            if isinstance(e, AppApiException):
                raise e
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value,
                                      gettext(
                                          'Verification failed, please check whether the parameters are correct: {error}').format(
                                          error=str(e)))
            else:
                return False
        return True

    def encryption_dict(self, model: Dict[str, object]):
        return {**model, 'spark_api_secret': super().encryption(model.get('spark_api_secret', ''))}

    def get_model_params_setting_form(self, model_name):
        return XunFeiSuperHumanoidTTSModelParams()
