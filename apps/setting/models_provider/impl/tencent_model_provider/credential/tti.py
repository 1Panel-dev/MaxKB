# coding=utf-8
from langchain_core.messages import HumanMessage

from common import forms
from common.exception.app_exception import AppApiException
from common.forms import BaseForm, TooltipLabel
from setting.models_provider.base_model_provider import BaseModelCredential, ValidCode


class TencentTTIModelParams(BaseForm):
    Style = forms.SingleSelect(
        TooltipLabel('绘画风格', '不传默认使用201（日系动漫风格）'),
        required=True,
        default_value='201',
        option_list=[
            {'value': '000', 'label': '不限定风格'},
            {'value': '101', 'label': '水墨画'},
            {'value': '102', 'label': '概念艺术'},
            {'value': '103', 'label': '油画1'},
            {'value': '118', 'label': '油画2（梵高）'},
            {'value': '104', 'label': '水彩画'},
            {'value': '105', 'label': '像素画'},
            {'value': '106', 'label': '厚涂风格'},
            {'value': '107', 'label': '插图'},
            {'value': '108', 'label': '剪纸风格'},
            {'value': '109', 'label': '印象派1（莫奈）'},
            {'value': '119', 'label': '印象派2'},
            {'value': '110', 'label': '2.5D'},
            {'value': '111', 'label': '古典肖像画'},
            {'value': '112', 'label': '黑白素描画'},
            {'value': '113', 'label': '赛博朋克'},
            {'value': '114', 'label': '科幻风格'},
            {'value': '115', 'label': '暗黑风格'},
            {'value': '116', 'label': '3D'},
            {'value': '117', 'label': '蒸汽波'},
            {'value': '201', 'label': '日系动漫'},
            {'value': '202', 'label': '怪兽风格'},
            {'value': '203', 'label': '唯美古风'},
            {'value': '204', 'label': '复古动漫'},
            {'value': '301', 'label': '游戏卡通手绘'},
            {'value': '401', 'label': '通用写实风格'},
        ],
        value_field='value',
        text_field='label'
    )

    Resolution = forms.SingleSelect(
        TooltipLabel('生成图分辨率', '不传默认使用768:768。'),
        required=True,
        default_value='768:768',
        option_list=[
            {'value': '768:768', 'label': '768:768（1:1）'},
            {'value': '768:1024', 'label': '768:1024（3:4）'},
            {'value': '1024:768', 'label': '1024:768（4:3）'},
            {'value': '1024:1024', 'label': '1024:1024（1:1）'},
            {'value': '720:1280', 'label': '720:1280（9:16）'},
            {'value': '1280:720', 'label': '1280:720（16:9）'},
            {'value': '768:1280', 'label': '768:1280（3:5）'},
            {'value': '1280:768', 'label': '1280:768（5:3）'},
            {'value': '1080:1920', 'label': '1080:1920（9:16）'},
            {'value': '1920:1080', 'label': '1920:1080（16:9）'},
        ],
        value_field='value',
        text_field='label'
    )


class TencentTTIModelCredential(BaseForm, BaseModelCredential):
    REQUIRED_FIELDS = ['hunyuan_secret_id', 'hunyuan_secret_key']

    @classmethod
    def _validate_model_type(cls, model_type, provider, raise_exception=False):
        if not any(mt['value'] == model_type for mt in provider.get_model_type_list()):
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'{model_type} 模型类型不支持')
            return False
        return True

    @classmethod
    def _validate_credential_fields(cls, model_credential, raise_exception=False):
        missing_keys = [key for key in cls.REQUIRED_FIELDS if key not in model_credential]
        if missing_keys:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'{", ".join(missing_keys)} 字段为必填字段')
            return False
        return True

    def is_valid(self, model_type, model_name, model_credential, model_params, provider, raise_exception=False):
        if not (self._validate_model_type(model_type, provider, raise_exception) and
                self._validate_credential_fields(model_credential, raise_exception)):
            return False
        try:
            model = provider.get_model(model_type, model_name, model_credential, **model_params)
            model.check_auth()
        except Exception as e:
            if raise_exception:
                raise AppApiException(ValidCode.valid_error.value, f'校验失败,请检查参数是否正确: {str(e)}')
            return False
        return True

    def encryption_dict(self, model):
        return {**model, 'hunyuan_secret_key': super().encryption(model.get('hunyuan_secret_key', ''))}

    hunyuan_secret_id = forms.PasswordInputField('SecretId', required=True)
    hunyuan_secret_key = forms.PasswordInputField('SecretKey', required=True)

    def get_model_params_setting_form(self, model_name):
        return TencentTTIModelParams()
