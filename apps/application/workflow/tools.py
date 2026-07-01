# coding=utf-8
"""
    @project: MaxKB
    @Author：虎虎虎
    @file： tools.py
    @date：2026/6/29 18:44
    @desc:
"""


class Reasoning:
    def __init__(self, reasoning_content_start, reasoning_content_end):
        self.content = ""
        self.reasoning_content = ""
        self.all_content = ""
        self.reasoning_content_start_tag = reasoning_content_start
        self.reasoning_content_end_tag = reasoning_content_end
        self.reasoning_content_start_tag_len = len(
            reasoning_content_start) if reasoning_content_start is not None else 0
        self.reasoning_content_end_tag_len = len(reasoning_content_end) if reasoning_content_end is not None else 0
        self.reasoning_content_end_tag_prefix = reasoning_content_end[
            0] if self.reasoning_content_end_tag_len > 0 else ''
        self.reasoning_content_is_start = False
        self.reasoning_content_is_end = False
        self.reasoning_content_chunk = ""

    def get_end_reasoning_content(self):
        if not self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': self.all_content, 'reasoning_content': ''}
            self.reasoning_content_chunk = ""
            return r
        if self.reasoning_content_is_start and not self.reasoning_content_is_end:
            r = {'content': '', 'reasoning_content': self.reasoning_content_chunk}
            self.reasoning_content_chunk = ""
            return r
        return {'content': '', 'reasoning_content': ''}

    def get_reasoning_content(self, chunk):
        # 如果没有开始思考过程标签那么就全是结果
        if self.reasoning_content_start_tag is None or len(self.reasoning_content_start_tag) == 0:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': ''}
        # 如果没有结束思考过程标签那么就全部是思考过程
        if self.reasoning_content_end_tag is None or len(self.reasoning_content_end_tag) == 0:
            return {'content': '', 'reasoning_content': chunk.content}
        self.all_content += chunk.content
        if not self.reasoning_content_is_start and len(self.all_content) >= self.reasoning_content_start_tag_len:
            if self.all_content.startswith(self.reasoning_content_start_tag):
                self.reasoning_content_is_start = True
                self.reasoning_content_chunk = self.all_content[self.reasoning_content_start_tag_len:]
            else:
                if not self.reasoning_content_is_end:
                    self.reasoning_content_is_end = True
                    self.content += self.all_content
                    return {'content': self.all_content, 'reasoning_content': ''}
        else:
            if self.reasoning_content_is_start:
                self.reasoning_content_chunk += chunk.content
        reasoning_content_end_tag_prefix_index = self.reasoning_content_chunk.find(
            self.reasoning_content_end_tag_prefix)
        if self.reasoning_content_is_end:
            self.content += chunk.content
            return {'content': chunk.content, 'reasoning_content': ''}
        # 是否包含结束
        if reasoning_content_end_tag_prefix_index > -1:
            if len(self.reasoning_content_chunk) - reasoning_content_end_tag_prefix_index >= self.reasoning_content_end_tag_len:
                reasoning_content_end_tag_index = self.reasoning_content_chunk.find(self.reasoning_content_end_tag)
                if reasoning_content_end_tag_index > -1:
                    reasoning_content_chunk = self.reasoning_content_chunk[0:reasoning_content_end_tag_index]
                    content_chunk = self.reasoning_content_chunk[
                                    reasoning_content_end_tag_index + self.reasoning_content_end_tag_len:]
                    self.reasoning_content += reasoning_content_chunk
                    self.content += content_chunk
                    self.reasoning_content_chunk = ""
                    self.reasoning_content_is_end = True
                    return {'content': content_chunk, 'reasoning_content': reasoning_content_chunk}
                else:
                    reasoning_content_chunk = self.reasoning_content_chunk[0:reasoning_content_end_tag_prefix_index + 1]
                    self.reasoning_content_chunk = self.reasoning_content_chunk.replace(reasoning_content_chunk, '')
                    self.reasoning_content += reasoning_content_chunk
                    return {'content': '', 'reasoning_content': reasoning_content_chunk}
            else:
                return {'content': '', 'reasoning_content': ''}

        else:
            if self.reasoning_content_is_end:
                self.content += chunk.content
                return {'content': chunk.content, 'reasoning_content': ''}
            else:
                # aaa
                result = {'content': '', 'reasoning_content': self.reasoning_content_chunk}
                self.reasoning_content += self.reasoning_content_chunk
                self.reasoning_content_chunk = ""
                return result
