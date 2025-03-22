# coding=utf-8
"""
    @project: maxkb
    @Author：虎
    @file： __init__.py.py
    @date：2024/6/7 14:43
    @desc:
"""
from .ai_chat_step_node import *
from .application_node import BaseApplicationNode
from .condition_node import *
from .direct_reply_node import *
from .form_node import *
from .function_lib_node import *
from .function_node import *
from .question_node import *
from .reranker_node import *

from .document_extract_node import *
from .image_understand_step_node import *
from .image_generate_step_node import *

from .search_dataset_node import *
from .speech_to_text_step_node import BaseSpeechToTextNode
from .start_node import *
from .text_to_speech_step_node.impl.base_text_to_speech_node import BaseTextToSpeechNode
from .variable_assign_node import BaseVariableAssignNode
from .mcp_node import BaseMcpNode

node_list = [BaseStartStepNode, BaseChatNode, BaseSearchDatasetNode, BaseQuestionNode,
             BaseConditionNode, BaseReplyNode,
             BaseFunctionNodeNode, BaseFunctionLibNodeNode, BaseRerankerNode, BaseApplicationNode,
             BaseDocumentExtractNode,
             BaseImageUnderstandNode, BaseFormNode, BaseSpeechToTextNode, BaseTextToSpeechNode,
             BaseImageGenerateNode, BaseVariableAssignNode, BaseMcpNode]


def get_node(node_type):
    find_list = [node for node in node_list if node.type == node_type]
    if len(find_list) > 0:
        return find_list[0]
    return None
