# -*- coding: utf-8 -*-
from django.test import SimpleTestCase

from models_provider.impl.tencent_model_provider.tencent_model_provider import TencentModelProvider


class TencentModelProviderTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.provider = TencentModelProvider()

    def test_stt_model_type_is_exposed(self):
        model_types = {item.get("value") for item in self.provider.get_model_type_list()}
        self.assertIn("STT", model_types)

    def test_stt_default_credential_without_model_name(self):
        # model_form 在未选择基础模型（model_name 为空）时应返回默认 STT 凭证，
        # 否则 create-model 流程会以“模型不支持”报 500。
        credential = self.provider.get_model_credential("STT", "")
        self.assertIsNotNone(credential)
        self.assertTrue(credential.to_form_list())

    def test_wand_asr_v1_uses_tokenhub_credential(self):
        from models_provider.impl.tencent_model_provider.credential.tokenhub_stt import (
            TencentTokenhubSTTModelCredential,
        )

        credential = self.provider.get_model_credential("STT", "wand-asr-v1")
        self.assertIsInstance(credential, TencentTokenhubSTTModelCredential)
        fields = {item.get("field") for item in credential.to_form_list()}
        self.assertIn("api_key", fields)
