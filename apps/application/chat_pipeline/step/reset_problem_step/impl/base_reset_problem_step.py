# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_reset_problem_step.py
    @date：2024/1/10 14:35
    @desc:
"""
from typing import List

from langchain.schema import HumanMessage

from application.chat_pipeline.step.reset_problem_step.i_reset_problem_step import IResetProblemStep
from application.models import ChatRecord
from common.util.split_model import flat_map
from setting.models_provider.tools import get_model_instance_by_model_user_id

prompt = (
    '()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在<data></data>标签中')


class BaseResetProblemStep(IResetProblemStep):
    def execute(self, problem_text: str, history_chat_record: List[ChatRecord] = None, model_id: str = None,
                problem_optimization_prompt=None,
                user_id=None,
                **kwargs) -> str:
        chat_model = get_model_instance_by_model_user_id(model_id, user_id) if model_id is not None else None
        start_index = len(history_chat_record) - 3
        history_message = [[history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
                           for index in
                           range(start_index if start_index > 0 else 0, len(history_chat_record))]
        reset_prompt = problem_optimization_prompt if problem_optimization_prompt else prompt
        message_list = [*flat_map(history_message),
                        HumanMessage(content=reset_prompt.replace('{question}', problem_text))]
        response = chat_model.invoke(message_list)
        padding_problem = problem_text
        if response.content.__contains__("<data>") and response.content.__contains__('</data>'):
            padding_problem_data = response.content[
                                   response.content.index('<data>') + 6:response.content.index('</data>')]
            if padding_problem_data is not None and len(padding_problem_data.strip()) > 0:
                padding_problem = padding_problem_data
        elif len(response.content) > 0:
            padding_problem = response.content

        try:
            request_token = chat_model.get_num_tokens_from_messages(message_list)
            response_token = chat_model.get_num_tokens(padding_problem)
        except Exception as e:
            request_token = 0
            response_token = 0
        self.context['message_tokens'] = request_token
        self.context['answer_tokens'] = response_token
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
