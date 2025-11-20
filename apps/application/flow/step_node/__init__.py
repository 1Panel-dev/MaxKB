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
from .data_source_local_node.impl.base_data_source_local_node import BaseDataSourceLocalNode
from .data_source_web_node.impl.base_data_source_web_node import BaseDataSourceWebNode
from .direct_reply_node import *
from .document_extract_node import *
from .form_node import *
from .image_generate_step_node import *
from .image_to_video_step_node import BaseImageToVideoNode
from .image_understand_step_node import *
from .intent_node import *
from .knowledge_write_node.impl.base_knowledge_write_node import BaseKnowledgeWriteNode
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
from .document_split_node import BaseDocumentSplitNode

node_list = [BaseStartStepNode, BaseChatNode, BaseSearchKnowledgeNode, BaseSearchDocumentNode, BaseQuestionNode,
             BaseConditionNode, BaseReplyNode,
             BaseToolNodeNode, BaseToolLibNodeNode, BaseRerankerNode, BaseApplicationNode,
             BaseDocumentExtractNode,
             BaseImageUnderstandNode, BaseFormNode, BaseSpeechToTextNode, BaseTextToSpeechNode,
             BaseImageGenerateNode, BaseVariableAssignNode, BaseMcpNode, BaseTextToVideoNode, BaseImageToVideoNode,
             BaseVideoUnderstandNode,
             BaseIntentNode, BaseLoopNode, BaseLoopStartStepNode,
             BaseLoopContinueNode,
             BaseLoopBreakNode, BaseVariableSplittingNode, BaseParameterExtractionNode, BaseVariableAggregationNode,
             BaseDataSourceLocalNode, BaseDataSourceWebNode, BaseKnowledgeWriteNode, BaseDocumentSplitNode]

node_map = {n.type: {w: n for w in n.support} for n in node_list}


def get_node(node_type, workflow_model):
    return node_map.get(node_type).get(workflow_model)
