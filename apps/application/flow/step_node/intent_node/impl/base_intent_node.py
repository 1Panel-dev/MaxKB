# coding=utf-8
import json
import re
import time
from typing import List, Dict, Any
from functools import reduce

from django.db.models import QuerySet
from langchain.schema import HumanMessage, SystemMessage

from application.flow.i_step_node import INode, NodeResult
from application.flow.step_node.intent_node.i_intent_node import IIntentNode
from models_provider.models import Model
from models_provider.tools import get_model_instance_by_model_workspace_id, get_model_credential
from .prompt_template import PROMPT_TEMPLATE

def get_default_model_params_setting(model_id):

    model = QuerySet(Model).filter(id=model_id).first()
    credential = get_model_credential(model.provider, model.model_type, model.model_name)
    model_params_setting = credential.get_model_params_setting_form(
        model.model_name).get_default_form_data()
    return model_params_setting


def _write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow, answer: str):

    chat_model = node_variable.get('chat_model')
    message_tokens = chat_model.get_num_tokens_from_messages(node_variable.get('message_list'))
    answer_tokens = chat_model.get_num_tokens(answer)

    node.context['message_tokens'] = message_tokens
    node.context['answer_tokens'] = answer_tokens
    node.context['answer'] = answer
    node.context['history_message'] = node_variable['history_message']
    node.context['user_input'] = node_variable['user_input']
    node.context['branch_id'] = node_variable.get('branch_id')
    node.context['reason'] = node_variable.get('reason')
    node.context['category'] = node_variable.get('category')
    node.context['run_time'] = time.time() - node.context['start_time']


def write_context(node_variable: Dict, workflow_variable: Dict, node: INode, workflow):

    response = node_variable.get('result')
    answer = response.content
    _write_context(node_variable, workflow_variable, node, workflow, answer)


class BaseIntentNode(IIntentNode):


    def save_context(self, details, workflow_manage):

        self.context['branch_id'] = details.get('branch_id')
        self.context['category'] = details.get('category')


    def execute(self, model_id, dialogue_number, history_chat_record, user_input, branch,
                model_params_setting=None, **kwargs) -> NodeResult:

        # 设置默认模型参数
        if model_params_setting is None:
            model_params_setting = get_default_model_params_setting(model_id)

        # 获取模型实例
        workspace_id = self.workflow_manage.get_body().get('workspace_id')
        chat_model = get_model_instance_by_model_workspace_id(
            model_id, workspace_id, **model_params_setting
        )

        # 获取历史对话
        history_message = self.get_history_message(history_chat_record, dialogue_number)
        self.context['history_message'] = history_message

        # 保存问题到上下文
        self.context['user_input'] = user_input

        # 构建分类提示词
        prompt = self.build_classification_prompt(user_input, branch)


        # 生成消息列表
        system = self.build_system_prompt()
        message_list = self.generate_message_list(system, prompt, history_message)
        self.context['message_list'] = message_list

        # 调用模型进行分类
        try:
            r = chat_model.invoke(message_list)
            classification_result = r.content.strip()

            # 解析分类结果获取分支信息
            matched_branch = self.parse_classification_result(classification_result, branch)

            #  返回结果
            return NodeResult({
                'result': r,
                'chat_model': chat_model,
                'message_list': message_list,
                'history_message': history_message,
                'user_input': user_input,
                'branch_id': matched_branch['id'],
                'reason': json.loads(r.content).get('reason'),
                'category': matched_branch.get('content', matched_branch['id'])
            }, {}, _write_context=write_context)

        except Exception as e:
            # 错误处理：返回"其他"分支
            other_branch = self.find_other_branch(branch)
            if other_branch:
                return NodeResult({
                    'branch_id': other_branch['id'],
                    'category': other_branch.get('content', other_branch['id']),
                    'error': str(e)
                }, {})
            else:
                raise Exception(f"error: {str(e)}")

    @staticmethod
    def get_history_message(history_chat_record, dialogue_number):
        """获取历史消息"""
        start_index = len(history_chat_record) - dialogue_number
        history_message = reduce(lambda x, y: [*x, *y], [
            [history_chat_record[index].get_human_message(), history_chat_record[index].get_ai_message()]
            for index in
            range(start_index if start_index > 0 else 0, len(history_chat_record))], [])

        for message in history_message:
            if isinstance(message.content, str):
                message.content = re.sub('<form_rander>[\d\D]*?<\/form_rander>', '', message.content)
        return history_message


    def build_system_prompt(self) -> str:
        """构建系统提示词"""
        return "你是一个专业的意图识别助手，请根据用户输入和意图选项，准确识别用户的真实意图。"

    def build_classification_prompt(self, user_input: str, branch: List[Dict]) -> str:
        """构建分类提示词"""

        classification_list = []

        other_branch = self.find_other_branch(branch)
        # 添加其他分支
        if other_branch:
            classification_list.append({
                "classificationId": 0,
                "content": other_branch.get('content')
            })
        # 添加正常分支
        classification_id = 1
        for b in branch:
            if not b.get('isOther'):
                classification_list.append({
                    "classificationId": classification_id,
                    "content": b['content']
                })
                classification_id += 1

        return PROMPT_TEMPLATE.format(
            classification_list=classification_list,
            user_input=user_input
        )


    def generate_message_list(self, system: str, prompt: str, history_message):
        """生成消息列表"""
        if system is None or len(system) == 0:
            return [*history_message, HumanMessage(self.workflow_manage.generate_prompt(prompt))]
        else:
            return [SystemMessage(self.workflow_manage.generate_prompt(system)), *history_message,
                    HumanMessage(self.workflow_manage.generate_prompt(prompt))]

    def parse_classification_result(self, result: str, branch: List[Dict]) -> Dict[str, Any]:
        """解析分类结果"""

        other_branch = self.find_other_branch(branch)
        normal_intents = [
            b
            for b in branch
            if not b.get('isOther')
        ]

        def get_branch_by_id(category_id: int):
            if category_id == 0:
                return other_branch
            elif 1 <= category_id <= len(normal_intents):
                return normal_intents[category_id - 1]
            return None

        try:
            result_json = json.loads(result)
            classification_id = result_json.get('classificationId', 0) # 0 兜底
            # 如果是 0 ，返回其他分支
            matched_branch = get_branch_by_id(classification_id)
            if matched_branch:
                return matched_branch

        except Exception as e:
            # json 解析失败，re 提取
            numbers = re.findall(r'"classificationId":\s*(\d+)', result)
            if numbers:
                classification_id = int(numbers[0])

                matched_branch = get_branch_by_id(classification_id)
                if matched_branch:
                    return matched_branch

        # 如果都解析失败，返回“other”
        return other_branch or (normal_intents[0] if normal_intents else {'id': 'unknown', 'content': 'unknown'})


    def find_other_branch(self, branch: List[Dict]) -> Dict[str, Any] | None:
        """查找其他分支"""
        for b in branch:
            if b.get('isOther'):
                return b
        return None


    def get_details(self, index: int, **kwargs):
        """获取节点执行详情"""
        return {
            'name': self.node.properties.get('stepName'),
            'index': index,
            'run_time': self.context.get('run_time'),
            'system': self.context.get('system'),
            'history_message': [
                {'content': message.content, 'role': message.type}
                for message in (self.context.get('history_message') or [])
            ],
            'user_input': self.context.get('user_input'),
            'answer': self.context.get('answer'),
            'branch_id': self.context.get('branch_id'),
            'category': self.context.get('category'),
            'type': self.node.type,
            'message_tokens': self.context.get('message_tokens'),
            'answer_tokens': self.context.get('answer_tokens'),
            'status': self.status,
            'err_message': self.err_message
        }