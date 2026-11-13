from django.test import SimpleTestCase

from models_provider.constants.model_provider_constants import ModelProvideConstants


class ProviderDefaultUrlTests(SimpleTestCase):
    """供应商创建模型表单中的 API 地址应展示官方默认值。"""

    def _url_default(self, provider_key, model_type, model_name, field):
        provider = ModelProvideConstants[provider_key]
        form_list = provider.get_model_credential(model_type, model_name).to_form_list()
        fields = {item["field"]: item for item in form_list}
        return fields[field].get("default_value")

    def test_providers_expose_default_url(self):
        cases = (
            # OpenAI
            ("model_openai_provider", "LLM", "gpt-4o", "api_base", "https://api.openai.com/v1"),
            ("model_openai_provider", "STT", "whisper-1", "api_base", "https://api.openai.com/v1"),
            ("model_openai_provider", "TTS", "tts-1", "api_base", "https://api.openai.com/v1"),
            ("model_openai_provider", "EMBEDDING", "text-embedding-3-small", "api_base", "https://api.openai.com/v1"),
            ("model_openai_provider", "IMAGE", "gpt-4o", "api_base", "https://api.openai.com/v1"),
            ("model_openai_provider", "TTI", "dall-e-3", "api_base", "https://api.openai.com/v1"),
            # Anthropic
            (
                "model_anthropic_provider",
                "LLM",
                "claude-3-5-sonnet-20241022",
                "api_base",
                "https://api.anthropic.com/v1",
            ),
            (
                "model_anthropic_provider",
                "IMAGE",
                "claude-3-5-sonnet-20241022",
                "api_base",
                "https://api.anthropic.com/v1",
            ),
            # Kimi
            ("model_kimi_provider", "LLM", "moonshot-v1-128k", "api_base", "https://api.moonshot.cn/v1"),
            # SiliconCloud
            (
                "model_siliconCloud_provider",
                "LLM",
                "deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
                "api_base",
                "https://api.siliconflow.cn/v1",
            ),
            (
                "model_siliconCloud_provider",
                "STT",
                "FunAudioLLM/SenseVoiceSmall",
                "api_base",
                "https://api.siliconflow.cn/v1",
            ),
            (
                "model_siliconCloud_provider",
                "EMBEDDING",
                "BAAI/bge-large-zh-v1.5",
                "api_base",
                "https://api.siliconflow.cn/v1",
            ),
            (
                "model_siliconCloud_provider",
                "TTI",
                "stabilityai/stable-diffusion-xl-base-1.0",
                "api_base",
                "https://api.siliconflow.cn/v1",
            ),
            (
                "model_siliconCloud_provider",
                "RERANKER",
                "BAAI/bge-reranker-v2-m3",
                "api_base",
                "https://api.siliconflow.cn/v1",
            ),
            (
                "model_siliconCloud_provider",
                "TTS",
                "FunAudioLLM/CosyVoice2-0.5B",
                "api_base",
                "https://api.siliconflow.cn/v1",
            ),
            (
                "model_siliconCloud_provider",
                "IMAGE",
                "Qwen/Qwen3-VL-32B-Instruct",
                "api_base",
                "https://api.siliconflow.cn/v1",
            ),
            # Aliyun BaiLian
            (
                "aliyun_bai_lian_model_provider",
                "LLM",
                "qwen3.7-plus",
                "api_base",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
            ("aliyun_bai_lian_model_provider", "STT", "default", "api_url", "https://dashscope.aliyuncs.com/api/v1"),
            (
                "aliyun_bai_lian_model_provider",
                "STT",
                "qwen-omni-turbo",
                "api_url",
                "https://dashscope.aliyuncs.com/api/v1",
            ),
            (
                "aliyun_bai_lian_model_provider",
                "STT",
                "qwen-audio-asr",
                "api_url",
                "https://dashscope.aliyuncs.com/api/v1",
            ),
            # Volcanic engine
            (
                "model_volcanic_engine_provider",
                "LLM",
                "ep-xxxxxxxxxx-yyyy",
                "api_base",
                "https://ark.cn-beijing.volces.com/api/v3",
            ),
            (
                "model_volcanic_engine_provider",
                "IMAGE",
                "ep-xxxxxxxxxx-yyyy",
                "api_base",
                "https://ark.cn-beijing.volces.com/api/v3",
            ),
            (
                "model_volcanic_engine_provider",
                "EMBEDDING",
                "ep-xxxxxxxxxx-yyyy",
                "api_base",
                "https://ark.cn-beijing.volces.com/api/v3",
            ),
            # Xunfei
            ("model_xf_provider", "LLM", "general", "spark_api_url", "wss://spark-api.xf-yun.com/v3.5/chat"),
            # Qianfan reranker
            ("model_qianfan_provider", "RERANKER", "bce-reranker-base", "api_url", "https://qianfan.baidubce.com/v2"),
        )

        for provider_key, model_type, model_name, field, expected in cases:
            with self.subTest(provider=provider_key, model_type=model_type, model_name=model_name, field=field):
                self.assertEqual(expected, self._url_default(provider_key, model_type, model_name, field))
