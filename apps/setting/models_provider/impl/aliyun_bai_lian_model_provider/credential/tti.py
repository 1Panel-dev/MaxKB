# coding=utf-8
"""
    @project: MaxKB
    @Author：虎
    @file： llm.py
    @date：2024/7/11 18:41
    @desc:
"""
import traceback
from typing import Dict

from django.utils.translation import gettext_lazy as _, gettext

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class QwenModelParams(BaseForm):
    size = forms.SingleSelect(
        TooltipLabel(_('Image size'), _('Specify the size of the generated image, such as: 1024x1024')),
        required=True,
        default_value='1024*1024',
        option_list=[
            {'value': '1024*1024', 'label': '1024*1024'},
            {'value': '720*1280', 'label': '720*1280'},
            {'value': '768*1152', 'label': '768*1152'},
            {'value': '1280*720', 'label': '1280*720'},
        ],
        text_field='label',
        value_field='value')
    n = forms.SliderField(
        TooltipLabel(_('Number of pictures'), _('Specify the number of generated images')),
        required=True, default_value=1,
        _min=1,
        _max=4,
        _step=1,
        precision=0)
    style = forms.SingleSelect(
        TooltipLabel(_('Style'), _('Specify the style of generated images')),
        required=True,
        default_value='<auto>',
        option_list=[
            {'value': '<auto>', 'label': _('Default value, the image style is randomly output by the model')},
            {'value': '<photography>', 'label': _('photography')},
            {'value': '<portrait>', 'label': _('Portraits')},
            {'value': '<3d cartoon>', 'label': _('3D cartoon')},
            {'value': '<anime>', 'label': _('animation')},
            {'value': '<oil painting>', 'label': _('painting')},
            {'value': '<watercolor>', 'label': _('watercolor')},
            {'value': '<sketch>', 'label': _('sketch')},
            {'value': '<chinese painting>', 'label': _('Chinese painting')},
            {'value': '<flat illustration>', 'label': _('flat illustration')},
        ],
        text_field='label',
        value_field='value'
    )


class QwenTextToImageModelCredential(BaseForm, BaseModelCredential):

    def is_valid(self, model_type: str, model_name, model_credential: Dict[str, object], model_params, provider,
                 raise_exception=False):
        model_type_list = provider.get_model_type_list()
        if not any(list(filter(lambda mt: mt.get('value') == model_type, model_type_list))):
            raise AppApiException(ValidCode.valid_error.value,
                                  gettext('{model_type} Model type is not supported').format(model_type=model_type))
        for key in ['api_key']:
            if key not in model_credential:
                if raise_exception:
                    raise AppApiException(ValidCode.valid_error.value, gettext('{key}  is required').format(key=key))
                else:
                    return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            res = model.check_auth()
            print(res)
        except Exception as e:
            traceback.print_exc()
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
        return {**model, 'api_key': super().encryption(model.get('api_key', ''))}

    api_key = forms.PasswordInputField('API Key', required=True)

    def get_model_params_setting_form(self, model_name):
        return QwenModelParams()
