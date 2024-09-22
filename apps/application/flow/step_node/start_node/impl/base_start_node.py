# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： base_start_node.py
    @date：2024/6/3 17:17
    @desc:
"""
import time
from datetime import datetime

from application.flow.i_step_node import NodeResult
from application.flow.step_node.start_node.i_start_node import IStarNode


class BaseStartStepNode(IStarNode):
    def execute(self, question, **kwargs) -> NodeResult:
        history_chat_record = self.flow_params_serializer.data.get('history_chat_record', [])
        history_context = [{'question': chat_record.problem_text, 'answer': chat_record.answer_text} for chat_record in
                           history_chat_record]
        chat_id = self.flow_params_serializer.data.get('chat_id')
        """
        开始节点 初始化全局变量
        """
        return NodeResult({'question': question},
                          {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'start_time': time.time(),
                           'history_context': history_context, 'chat_id': str(chat_id)})

    def get_details(self, index: int, **kwargs):
        global_fields = []
        for field in self.node.properties.get('config')['globalFields']:
            key = field['value']
            global_fields.append({
                'label': field['label'],
                'key': key,
                'value': self.workflow_manage[key] if key in self.workflow_manage else ''
            })
        return {
            'name': self.node.properties.get('stepName'),
            "index": index,
            "question": self.context.get('question'),
            'run_time': self.context.get('run_time'),
            'type': self.node.type,
            'status': self.status,
            'err_message': self.err_message,
            'global_fields': global_fields
        }
