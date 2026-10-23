# coding=utf-8
"""
@project: MaxKB
@Author：虎虎虎
@file： partial_json.py
@date：2026/10/23
@desc: 宽松 JSON 解析补全器,与前端 extract-partial-json 对应

适用场景:流式拼接的 LLM tool_call.arguments,可能在任意位置被截断,或带有模型生成的非法转义。
- 截断的字符串保留已有部分(含截断在转义、\\uXXXX、代理对中间的情况)
- 截断的键、只有键没有值、截断的 true/false/null 整个字段丢弃
- 截断的数字取已有的合法部分(1. -> 1)
- 未闭合的对象/数组自动补全
- 非法转义:\\' 视为 ',其余(如 \\d)保留反斜杠,避免改变代码/正则语义
- 字符串内的原始控制字符(换行、制表符)直接保留
"""

import json
import re

_WHITESPACE = " \t\n\r"
_ESCAPES = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t", "'": "'"}
_LITERALS = {"true": True, "false": False, "null": None}
_HEX4 = re.compile(r"[0-9a-fA-F]{4}")
_HEX_PREFIX = re.compile(r"[0-9a-fA-F]{0,3}")
_STRING_PLAIN = re.compile(r'[^"\\]*')
_NUMBER = re.compile(r"-?\d*(?:\.\d*)?(?:[eE][+-]?\d*)?")
# 值缺失:截断在值开始之前或值无法补全,所在字段整体丢弃
_MISSING = object()


class _Parser:
    def __init__(self, text: str):
        self.s = text
        self.n = len(text)
        self.i = 0

    def skip_whitespace(self):
        while self.i < self.n and self.s[self.i] in _WHITESPACE:
            self.i += 1

    def value(self):
        self.skip_whitespace()
        if self.i >= self.n:
            return _MISSING
        c = self.s[self.i]
        if c == "{":
            return self.object()
        if c == "[":
            return self.array()
        if c == '"':
            return self.string()[0]
        if c == "-" or c.isdigit():
            return self.number()
        return self.literal()

    def object(self):
        self.i += 1
        result = {}
        while True:
            self.skip_whitespace()
            if self.i >= self.n:
                return result
            c = self.s[self.i]
            if c == "}":
                self.i += 1
                return result
            if c == ",":
                self.i += 1
                continue
            if c != '"':
                raise ValueError(f"Expecting property name at char {self.i}")
            key, closed = self.string()
            if not closed:
                return result
            self.skip_whitespace()
            if self.i >= self.n:
                return result
            if self.s[self.i] != ":":
                raise ValueError(f"Expecting ':' at char {self.i}")
            self.i += 1
            value = self.value()
            if value is _MISSING:
                return result
            result[key] = value

    def array(self):
        self.i += 1
        result = []
        while True:
            self.skip_whitespace()
            if self.i >= self.n:
                return result
            c = self.s[self.i]
            if c == "]":
                self.i += 1
                return result
            if c == ",":
                self.i += 1
                continue
            value = self.value()
            if value is _MISSING:
                return result
            result.append(value)

    def string(self):
        """返回 (值, 是否正常闭合);截断时返回已解析部分"""
        s = self.s
        self.i += 1
        parts = []
        start = self.i
        while True:
            # 流式过程中每个分片都会重新解析,普通字符整段跳过
            self.i = _STRING_PLAIN.match(s, self.i).end()
            if self.i >= self.n:
                break
            if s[self.i] == '"':
                parts.append(s[start : self.i])
                self.i += 1
                return "".join(parts), True
            parts.append(s[start : self.i])
            if self.i + 1 >= self.n:
                self.i = self.n
                return "".join(parts), False
            escape = s[self.i + 1]
            if escape == "u":
                char, consumed = self.unicode_escape(self.i)
                if char is None:
                    # \uXXXX 被截断,丢弃不完整的转义
                    self.i = self.n
                    return "".join(parts), False
                parts.append(char)
                self.i += consumed
            elif escape in _ESCAPES:
                parts.append(_ESCAPES[escape])
                self.i += 2
            else:
                parts.append("\\" + escape)
                self.i += 2
            start = self.i
        parts.append(s[start : self.i])
        return "".join(parts), False

    def unicode_escape(self, at: int):
        """解析 at 处的 \\uXXXX(含代理对),返回 (字符, 消耗长度);截断返回 (None, 0)"""
        s = self.s
        hex4 = s[at + 2 : at + 6]
        if not _HEX4.fullmatch(hex4):
            if at + 6 > self.n and _HEX_PREFIX.fullmatch(hex4):
                return None, 0
            return "\\u", 2
        code = int(hex4, 16)
        if 0xD800 <= code < 0xDC00:
            low = s[at + 6 : at + 12]
            if low.startswith("\\u") and _HEX4.fullmatch(low[2:]) and 0xDC00 <= int(low[2:], 16) < 0xE000:
                return chr(0x10000 + ((code - 0xD800) << 10) + (int(low[2:], 16) - 0xDC00)), 12
            # 高位代理后被截断,低位代理还没到
            if at + 12 > self.n and "\\u".startswith(low[:2]) and _HEX_PREFIX.fullmatch(low[2:]):
                return None, 0
        return chr(code), 6

    def number(self):
        match = _NUMBER.match(self.s, self.i)
        text = match.group()
        self.i = match.end()
        # 截断的数字去掉末尾不完整部分:1. / 1e / 1e- / -
        while text:
            try:
                return json.loads(text)
            except ValueError:
                text = text[:-1]
        return _MISSING

    def literal(self):
        rest = self.s[self.i : self.i + 5]
        for word, value in _LITERALS.items():
            if rest.startswith(word):
                self.i += len(word)
                return value
            if self.i + len(rest) >= self.n and rest and word.startswith(rest):
                self.i = self.n
                return _MISSING
        raise ValueError(f"Unexpected character {self.s[self.i]!r} at char {self.i}")


def parse_partial_json(text: str, *, strict: bool = False):
    """
    解析可能不完整的 JSON,补全截断部分;无法解析时抛 ValueError。
    签名与 langchain_core.utils.json.parse_partial_json 兼容,可直接替换。
    """
    if not isinstance(text, str):
        raise ValueError("JSON text must be a string")
    try:
        return json.loads(text, strict=strict)
    except ValueError:
        pass
    parser = _Parser(text)
    value = parser.value()
    if value is _MISSING:
        raise ValueError("Empty or incomplete JSON")
    return value


def complete_json(text: str) -> str:
    """补全为合法 JSON 字符串;本身合法时原样返回,无法解析时抛 ValueError"""
    try:
        json.loads(text)
        return text
    except ValueError:
        return json.dumps(parse_partial_json(text), ensure_ascii=False)
