# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2024/6/7 14:43
    @desc:
"""
from .ai_chat_step_node import *
from .condition_node import *
from .question_node import *
from .search_dataset_node import *
from .start_node import *
from .direct_reply_node import *

node_list = [BaseStartStepNode, BaseChatNode, BaseSearchDatasetNode, BaseQuestionNode, BaseConditionNode, BaseReplyNode]


def get_node(node_type):
    find_list = [node for node in node_list if node.type == node_type]
    if len(find_list) > 0:
        return find_list[0]
    return None
