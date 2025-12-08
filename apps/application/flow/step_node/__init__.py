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
from .document_extract_node import *
from .form_node import *
from .image_generate_step_node import *
from .image_to_video_step_node import BaseImageToVideoNode
from .image_understand_step_node import *
from .intent_node import *
from .loop_break_node import BaseLoopBreakNode
from .loop_continue_node import BaseLoopContinueNode
from .loop_node import *
from .loop_start_node import *
from .mcp_node import BaseMcpNode
from .parameter_extraction_node import BaseParameterExtractionNode
from .question_node import *
from .reranker_node import *
from .search_document_node import BaseSearchDocumentNode
from .search_knowledge_node import *
from .speech_to_text_step_node import BaseSpeechToTextNode
from .start_node import *
from .text_to_speech_step_node.impl.base_text_to_speech_node import BaseTextToSpeechNode
from .text_to_video_step_node.impl.base_text_to_video_node import BaseTextToVideoNode
from .tool_lib_node import *
from .tool_node import *
from .variable_aggregation_node.impl.base_variable_aggregation_node import BaseVariableAggregationNode
from .variable_assign_node import BaseVariableAssignNode
from .variable_splitting_node import BaseVariableSplittingNode
from .video_understand_step_node import BaseVideoUnderstandNode

node_list = [BaseStartStepNode, BaseChatNode, BaseSearchKnowledgeNode, BaseSearchDocumentNode, BaseQuestionNode,
             BaseConditionNode, BaseReplyNode,
             BaseToolNodeNode, BaseToolLibNodeNode, BaseRerankerNode, BaseApplicationNode,
             BaseDocumentExtractNode,
             BaseImageUnderstandNode, BaseFormNode, BaseSpeechToTextNode, BaseTextToSpeechNode,
             BaseImageGenerateNode, BaseVariableAssignNode, BaseMcpNode, BaseTextToVideoNode, BaseImageToVideoNode,
             BaseVideoUnderstandNode,
             BaseIntentNode, BaseLoopNode, BaseLoopStartStepNode,
             BaseLoopContinueNode,
             BaseLoopBreakNode, BaseVariableSplittingNode, BaseParameterExtractionNode, BaseVariableAggregationNode]


def get_node(node_type):
    find_list = [node for node in node_list if node.type == node_type]
    if len(find_list) > 0:
        return find_list[0]
    return None
