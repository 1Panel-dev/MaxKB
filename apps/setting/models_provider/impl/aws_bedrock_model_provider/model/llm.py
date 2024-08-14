from typing import List, Dict, Any, Optional, Iterator
from langchain_community.chat_models import BedrockChat
from langchain_community.chat_models.bedrock import ChatPromptAdapter
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.messages import BaseMessage, get_buffer_string, AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk
from setting.models_provider.base_model_provider import MaxKBBaseModel


class BedrockModel(MaxKBBaseModel, BedrockChat):

    @staticmethod
    def is_cache_model():
        return False

    def __init__(self, model_id: str, region_name: str, credentials_profile_name: str,
                 streaming: bool = False, **kwargs):
        super().__init__(model_id=model_id, region_name=region_name,
                         credentials_profile_name=credentials_profile_name, streaming=streaming, **kwargs)

    @classmethod
    def new_instance(cls, model_type: str, model_name: str, model_credential: Dict[str, str],
                     **model_kwargs) -> 'BedrockModel':
        optional_params = {}
        if 'max_tokens' in model_kwargs and model_kwargs['max_tokens'] is not None:
            optional_params['max_tokens'] = model_kwargs['max_tokens']
        if 'temperature' in model_kwargs and model_kwargs['temperature'] is not None:
            optional_params['temperature'] = model_kwargs['temperature']

        return cls(
            model_id=model_name,
            region_name=model_credential['region_name'],
            credentials_profile_name=model_credential['credentials_profile_name'],
            streaming=model_kwargs.pop('streaming', False),
            **optional_params
        )

    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        return sum(self._get_num_tokens(get_buffer_string([message])) for message in messages)

    def get_num_tokens(self, text: str) -> int:
        return self._get_num_tokens(text)

    def _stream(
            self,
            messages: List[BaseMessage],
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        provider = self._get_provider()
        prompt, system, formatted_messages = None, None, None

        if provider == "anthropic":
            system, formatted_messages = ChatPromptAdapter.format_messages(
                provider, messages
            )
        else:
            prompt = ChatPromptAdapter.convert_messages_to_prompt(
                provider=provider, messages=messages
            )

        for chunk in self._prepare_input_and_invoke_stream(
                prompt=prompt,
                system=system,
                messages=formatted_messages,
                stop=stop,
                run_manager=run_manager,
                **kwargs,
        ):
            delta = chunk.text
            yield ChatGenerationChunk(message=AIMessageChunk(content=delta))
