# coding=utf-8
import importlib
import threading
from typing import Iterator

# 供应商注册表：模型供应商不再用 Enum 硬编码实例，而是注册为"模块路径 + 类名"的
# 惰性工厂。__getitem__ 首次访问某供应商时才 importlib 加载对应模块并缓存实例，
# 因此导入 models_provider 时不会连带加载 21 个供应商的重依赖（openai/bedrock/
# gemini/azure 等），只在真正使用某个供应商时按需加载，从而加快启动、降低内存。


class _ProviderRegistry:
    def __init__(self):
        self._factories: dict[str, tuple[str, str]] = {}
        self._instances: dict[str, object] = {}
        self._lock = threading.Lock()

    def register(self, name: str, provider_dir: str, class_name: str) -> "_ProviderRegistry":
        self._factories[name] = (f"models_provider.impl.{provider_dir}.{provider_dir}", class_name)
        return self

    def __getitem__(self, name: str):
        instance = self._instances.get(name)
        if instance is None:
            with self._lock:
                instance = self._instances.get(name)
                if instance is None:
                    module_path, class_name = self._factories[name]
                    module = importlib.import_module(module_path)
                    instance = getattr(module, class_name)()
                    self._instances[name] = instance
        return instance

    def __iter__(self) -> Iterator[str]:
        return iter(self._factories)

    def __contains__(self, name: object) -> bool:
        return name in self._factories

    def __len__(self) -> int:
        return len(self._factories)

    @property
    def __members__(self) -> dict:
        return self._factories


ModelProvideConstants = (
    _ProviderRegistry()
    .register("model_azure_provider", "azure_model_provider", "AzureModelProvider")
    .register("model_qianfan_provider", "qianfan_model_provider", "QianfanModelProvider")
    .register("model_ollama_provider", "ollama_model_provider", "OllamaModelProvider")
    .register("model_openai_provider", "openai_model_provider", "OpenAIModelProvider")
    .register("model_docker_ai_provider", "docker_ai_model_provider", "DockerModelProvider")
    .register("model_kimi_provider", "kimi_model_provider", "KimiModelProvider")
    .register("model_zhipu_provider", "zhipu_model_provider", "ZhiPuModelProvider")
    .register("model_xf_provider", "xf_model_provider", "XunFeiModelProvider")
    .register("model_deepseek_provider", "deepseek_model_provider", "DeepSeekModelProvider")
    .register("model_gemini_provider", "gemini_model_provider", "GeminiModelProvider")
    .register("model_volcanic_engine_provider", "volcanic_engine_model_provider", "VolcanicEngineModelProvider")
    .register("model_tencent_provider", "tencent_model_provider", "TencentModelProvider")
    .register("model_aws_bedrock_provider", "aws_bedrock_model_provider", "BedrockModelProvider")
    .register("model_local_provider", "local_model_provider", "LocalModelProvider")
    .register("model_xinference_provider", "xinference_model_provider", "XinferenceModelProvider")
    .register("model_vllm_provider", "vllm_model_provider", "VllmModelProvider")
    .register("aliyun_bai_lian_model_provider", "aliyun_bai_lian_model_provider", "AliyunBaiLianModelProvider")
    .register("model_anthropic_provider", "anthropic_model_provider", "AnthropicModelProvider")
    .register("model_siliconCloud_provider", "siliconCloud_model_provider", "SiliconCloudModelProvider")
    .register("model_regolo_provider", "regolo_model_provider", "RegoloModelProvider")
    .register("model_minimax_provider", "minimax_model_provider", "MiniMaxModelProvider")
)
