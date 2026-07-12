# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_generate_human_message_step.py.py
    @date：2024/1/10 17:50
    @desc:
"""
from typing import List, Dict

from langchain_core.messages import SystemMessage, BaseMessage, HumanMessage

from application.chat_pipeline.I_base_chat_pipeline import ParagraphPipelineModel
from application.chat_pipeline.pipeline_manage import PipelineManage
from application.chat_pipeline.step.generate_human_message_step.i_generate_human_message_step import \
    IGenerateHumanMessageStep
from application.models import ChatRecord
from common.utils.common import flat_map


class BaseGenerateHumanMessageStep(IGenerateHumanMessageStep):

    def _run(self, manage: PipelineManage):
        # Pass through file-related context keys from manage.context to execute
        step_args = {**self.context['step_args']}
        for key in ['document_text', 'image_list', 'video_list', 'document_list', 'audio_list', 'other_list', 'processed_images', 'processed_videos', 'processed_audio']:
            if key in manage.context:
                step_args[key] = manage.context[key]
        message_list = self.execute(**step_args)
        manage.context['message_list'] = message_list

    def execute(self, problem_text: str,
                paragraph_list: List[ParagraphPipelineModel],
                history_chat_record: List[ChatRecord],
                dialogue_number: int,
                max_paragraph_char_number: int,
                prompt: str,
                padding_problem_text: str = None,
                no_references_setting=None,
                system=None,
                **kwargs) -> List[BaseMessage]:
        document_text = kwargs.get('document_text', '')
        processed_images = kwargs.get('processed_images', None)
        processed_videos = kwargs.get('processed_videos', None)
        processed_audio = kwargs.get('processed_audio', None)
        has_data = (paragraph_list is not None and len(paragraph_list) > 0) or bool(document_text)
        prompt = prompt if has_data else no_references_setting.get('value')
        exec_problem_text = padding_problem_text if padding_problem_text is not None else problem_text
        start_index = len(history_chat_record) - dialogue_number
        history_message = [[history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
                           for index in
                           range(start_index if start_index > 0 else 0, len(history_chat_record))]
        if system is not None and len(system) > 0:
            return [SystemMessage(system), *flat_map(history_message),
                    self.to_human_message(prompt, exec_problem_text, max_paragraph_char_number, paragraph_list,
                                          no_references_setting, document_text, processed_images, processed_videos, processed_audio)]

        return [*flat_map(history_message),
                self.to_human_message(prompt, exec_problem_text, max_paragraph_char_number, paragraph_list,
                                      no_references_setting, document_text, processed_images, processed_videos, processed_audio)]

    @staticmethod
    def to_human_message(prompt: str,
                         problem: str,
                         max_paragraph_char_number: int,
                         paragraph_list: List[ParagraphPipelineModel],
                         no_references_setting: Dict,
                         document_text: str = '',
                         processed_images: list = None,
                         processed_videos: list = None,
                         processed_audio: list = None):
        has_paragraphs = paragraph_list is not None and len(paragraph_list) > 0

        if not has_paragraphs and not document_text:
            if no_references_setting.get('status') == 'ai_questioning':
                text_content = no_references_setting.get('value').replace('{question}', problem)
            else:
                text_content = prompt.replace('{data}', "").replace('{question}', problem)
        else:
            temp_len = 0
            data_list = []
            if has_paragraphs:
                for p in paragraph_list:
                    content = f"{p.title}:{p.content}"
                    temp_len += len(content)
                    if temp_len > max_paragraph_char_number:
                        row_data = content[0:max_paragraph_char_number - temp_len]
                        data_list.append(f"<data>{row_data}</data>")
                        break
                    else:
                        data_list.append(f"<data>{content}</data>")

            if document_text:
                data_list.append(document_text)

            data = "\n".join(data_list)
            text_content = prompt.replace('{data}', data).replace('{question}', problem)

        # 收集所有多模态内容（图片、视频、音频）
        media_content = []
        if processed_images and len(processed_images) > 0:
            media_content.extend(processed_images)
        if processed_videos and len(processed_videos) > 0:
            media_content.extend(processed_videos)
        if processed_audio and len(processed_audio) > 0:
            media_content.extend(processed_audio)

        if media_content:
            content = [*media_content, {"type": "text", "text": text_content}]
            return HumanMessage(content=content)

        return HumanMessage(content=text_content)

    def get_details(self, manage, **kwargs):
        return {
            'status': self.status,
            'err_message': self.err_message,
            'step_type': 'generate_human_message',
        }
