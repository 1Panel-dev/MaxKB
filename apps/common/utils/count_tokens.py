from langchain_core.messages import get_buffer_string

from common.config.tokenizer_manage_config import TokenizerManage


def count_local_tokens(message_list, answer):
    """模型不可用时,用本地 tokenizer 估算输入/输出 token 数。"""
    tokenizer = TokenizerManage.get_tokenizer()
    message_tokens = sum([len(tokenizer.encode(get_buffer_string([m]))) for m in message_list])
    answer_tokens = len(tokenizer.encode(answer))
    return message_tokens, answer_tokens
