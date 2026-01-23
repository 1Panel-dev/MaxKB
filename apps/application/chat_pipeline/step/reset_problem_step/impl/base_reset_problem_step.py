# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_reset_problem_step.py
    @date：2024/1/10 14:35
    @desc:
"""
from typing import List

from django.utils.translation import gettext as _
from langchain.schema import HumanMessage

from application.chat_pipeline.step.reset_problem_step.i_reset_problem_step import IResetProblemStep
from application.models import ChatRecord
from common.utils.split_model import flat_map
from models_provider.tools import get_model_instance_by_model_workspace_id

prompt = _(
    "() contains the user's question. Answer the guessed user's question based on the context ({question}) Requirement: Output a complete question and put it in the <data></data> tag")


class BaseResetProblemStep(IResetProblemStep):
    def execute(self, problem_text: str, history_chat_record: List[ChatRecord] = None, model_id: str = None,
                problem_optimization_prompt=None,
                workspace_id=None,
                **kwargs) -> str:
        chat_model = get_model_instance_by_model_workspace_id(model_id, workspace_id) if model_id is not None else None
        if chat_model is None:
            return problem_text
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
        return {'status': self.status,
                'err_message': self.err_message,
                'step_type': 'problem_padding',
                'run_time': self.context['run_time'],
                'model_id': str(manage.context['model_id']) if 'model_id' in manage.context else None,
                'message_tokens': self.context.get('message_tokens', 0),
                'answer_tokens': self.context.get('answer_tokens', 0),
                'cost': 0,
                'padding_problem_text': self.context.get('padding_problem_text'),
                'problem_text': self.context.get("step_args").get('problem_text'),
                }
