# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_reset_problem_step.py
    @date：2024/1/10 14:35
    @desc:
"""
from typing import List

from langchain.chat_models.base import BaseChatModel
from langchain.schema import HumanMessage

from application.chat_pipeline.step.reset_problem_step.i_reset_problem_step import IResetProblemStep
from application.models import ChatRecord
from common.util.split_model import flat_map

prompt = (
    '()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在<data></data>标签中')


class BaseResetProblemStep(IResetProblemStep):
    def execute(self, problem_text: str, history_chat_record: List[ChatRecord] = None, chat_model: BaseChatModel = None,
                **kwargs) -> str:
        start_index = len(history_chat_record) - 3
        history_message = [[history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
                           for index in
                           range(start_index if start_index > 0 else 0, len(history_chat_record))]
        message_list = [*flat_map(history_message),
                        HumanMessage(content=prompt.format(**{'question': problem_text}))]
        response = chat_model.invoke(message_list)
        padding_problem = problem_text
        if response.content.__contains__("<data>") and response.content.__contains__('</data>'):
            padding_problem_data = response.content[
                                   response.content.index('<data>') + 6:response.content.index('</data>')]
            if padding_problem_data is not None and len(padding_problem_data.strip()) > 0:
                padding_problem = padding_problem_data
        self.context['message_tokens'] = chat_model.get_num_tokens_from_messages(message_list)
        self.context['answer_tokens'] = chat_model.get_num_tokens(padding_problem)
        return padding_problem

    def get_details(self, manage, **kwargs):
        return {
            'step_type': 'problem_padding',
            'run_time': self.context['run_time'],
            'model_id': str(manage.context['model_id']) if 'model_id' in manage.context else None,
            'message_tokens': self.context['message_tokens'],
            'answer_tokens': self.context['answer_tokens'],
            'cost': 0,
            'padding_problem_text': self.context.get('padding_problem_text'),
            'problem_text': self.context.get("step_args").get('problem_text'),
        }
