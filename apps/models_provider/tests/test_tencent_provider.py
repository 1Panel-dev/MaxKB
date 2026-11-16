# -*- coding: utf-8 -*-
from django.test import SimpleTestCase

from models_provider.base_model_provider import ModelTypeConst
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

    def test_dynamic_classify_vision_as_image(self):
        # TokenHub 的 /models 不带模态元数据，含 vision 的多模态理解模型应收敛到 IMAGE。
        for model_id in (
            "hy-vision-2.0-instruct",
            "hunyuan-t1-vision-20250916",
            "deepseek/deepseek-v4-flash-vision-exp",
        ):
            self.assertEqual(TencentModelProvider.classify_dynamic_model(model_id), ModelTypeConst.IMAGE)

    def test_dynamic_classify_yt_video_as_itv(self):
        self.assertEqual(TencentModelProvider.classify_dynamic_model("yt-video-humanactor"), ModelTypeConst.ITV)

    def test_dynamic_classify_vision_video_stays_ttv(self):
        # 带 video 的视觉模型仍是视频生成任务，不应被误判为视觉模型。
        self.assertEqual(
            TencentModelProvider.classify_dynamic_model("hunyuan-turbos-vision-video-20250728"),
            ModelTypeConst.TTV,
        )
