# coding=utf-8
"""
讯飞 TTS 工厂类 Credential，根据 api_version 路由到具体 Credential
"""
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from models_provider.base_model_provider import BaseModelCredential, ValidCode
from common.utils.logger import maxkb_logger


class XunFeiDefaultTTSModelCredential(BaseForm, BaseModelCredential):
    """讯飞 TTS 工厂类 Credential，根据 api_version 参数路由到具体实现"""

    api_version = forms.SingleSelect(
        _("API Version"), required=True,
        text_field='label',
        value_field='value',
        default_value='online',
        option_list=[
            {'label': _('Online TTS'), 'value': 'online'},
            {'label': _('Super Humanoid TTS'), 'value': 'super_humanoid'}
        ])

    spark_api_url = forms.TextInputField('API URL', required=True,
                                         default_value='wss://tts-api.xfyun.cn/v2/tts',
                                         relation_show_field_dict={"api_version": ["online"]})
    spark_api_url_super = forms.TextInputField('API URL', required=True,
                                               default_value='wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6',
                                               relation_show_field_dict={"api_version": ["super_humanoid"]})

    # vcn 选择放在 credential 中，根据 api_version 联动显示
    vcn_online = forms.SingleSelect(
        TooltipLabel(_('Speaker'), _('Speaker selection for standard TTS service')),
        required=True, default_value='xiaoyan',
        text_field='value',
        value_field='value',
        option_list=[
            {'text': _('iFlytek Xiaoyan'), 'value': 'xiaoyan'},
            {'text': _('iFlytek Xujiu'), 'value': 'aisjiuxu'},
            {'text': _('iFlytek Xiaoping'), 'value': 'aisxping'},
            {'text': _('iFlytek Xiaojing'), 'value': 'aisjinger'},
            {'text': _('iFlytek Xuxiaobao'), 'value': 'aisbabyxu'},
        ],
        relation_show_field_dict={"api_version": ["online"]})

    vcn_super = forms.SingleSelect(
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
        ],
        relation_show_field_dict={"api_version": ["super_humanoid"]})

    spark_app_id = forms.TextInputField('APP ID', required=True)
    spark_api_key = forms.PasswordInputField("API Key", required=True)
    spark_api_secret = forms.PasswordInputField('API Secret', required=True)

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))

        api_version = model_credential.get('api_version', 'online')
        if api_version == 'super_humanoid':
            required_keys = ['spark_api_url_super', 'spark_app_id', 'spark_api_key', 'spark_api_secret']
        else:
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
            maxkb_logger.error(f'Exception: {e}', exc_info=True)
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
        # params 只包含通用参数，vcn 已在 credential 中
        return XunFeiDefaultTTSModelParams()


class XunFeiDefaultTTSModelParams(BaseForm):
    """工厂类的参数表单，只包含通用参数"""

    speed = forms.SliderField(
        TooltipLabel(_('speaking speed'), _('Speech speed, optional value: [0-100], default is 50')),
        required=True, default_value=50,
        _min=1,
        _max=100,
        _step=5,
        precision=1)
