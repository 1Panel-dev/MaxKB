# coding=utf-8
"""
@project: MaxKB
@file： token_ledger.py
@desc: AI 对话节点的 token 账本。

节点写出的内容按顺序经过 AIChatNode.write 交给账本：
- 已完成的模型调用：累加模型返回的用量（UsageContent）；
- 最后一条是回复（文本、思考、未拿到结果的工具调用），说明最后一次调用未完成（被停止 / 报错 / 模型不返回用量），
  用本地 tokenizer 估算：输入 = 初始消息 + 这段回复之前的全部内容，输出 = 这段回复。
用量与工具结果出现在一次调用结束之后，因此从末尾往前、遇到用量或工具结果为止的回复，就是未完成的那一次。
"""

from application.workflow.message.struct.reasoning_content import ReasoningContent
from application.workflow.message.struct.text_content import TextContent
from application.workflow.message.struct.tool_content import ToolContent
from application.workflow.message.struct.usage_content import UsageContent
from common.config.tokenizer_manage_config import TokenizerManage
from common.utils.count_tokens import count_local_tokens


def _text(content):
    if isinstance(content, ToolContent):
        return (content.arguments or "") + (content.content or "")
    if isinstance(content, (TextContent, ReasoningContent)):
        return content.content or ""
    return ""


def _is_reply(content):
    # 工具结果（content 有值）是下一次调用的输入，不是回复
    return isinstance(content, (TextContent, ReasoningContent)) or (
        isinstance(content, ToolContent) and not content.content
    )


class TokenLedger:
    def __init__(self):
        self._base_messages = []
        self._contents = []

    def set_base_messages(self, messages):
        """第一次调用的输入（系统提示词 + 历史消息 + 问题）。"""
        self._base_messages = list(messages)

    def record(self, content):
        # 空用量表示调用开始，还没回复就被停止也计入输入；其余只记有文本的内容（跳过空的结束标记）
        if isinstance(content, UsageContent) or _text(content):
            self._contents.append(content)

    def summarize(self) -> tuple[int, int]:
        """返回 (message_tokens, answer_tokens)。"""
        usages = {}
        for content in self._contents:
            if isinstance(content, UsageContent) and content.usage:
                # 同一次调用可能多个 chunk 都带用量（如每个 chunk 给累计值），逐字段取最大值
                usage = usages.setdefault(content.id, {})
                for field in ("input_tokens", "output_tokens"):
                    usage[field] = max(usage.get(field, 0), content.usage.get(field) or 0)
        message_tokens = sum(usage["input_tokens"] for usage in usages.values())
        answer_tokens = sum(usage["output_tokens"] for usage in usages.values())

        split = len(self._contents)
        while split and _is_reply(self._contents[split - 1]):
            split -= 1
        last = self._contents[-1] if self._contents else None
        if split < len(self._contents) or (isinstance(last, UsageContent) and not last.usage):
            tokenizer = TokenizerManage.get_tokenizer()
            before = "".join(_text(content) for content in self._contents[:split])
            reply = "".join(_text(content) for content in self._contents[split:])
            message_tokens += count_local_tokens(self._base_messages, "")[0] if self._base_messages else 0
            message_tokens += len(tokenizer.encode(before)) if before else 0
            answer_tokens += len(tokenizer.encode(reply)) if reply else 0
        return message_tokens, answer_tokens
