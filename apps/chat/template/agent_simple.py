import copy
import json

from django.db.models import QuerySet

template = {
    "edges": [
        {
            "id": "6a8d23d9-5179-424e-80c2-f08d37cdb8d4",
            "type": "app-edge",
            "endPoint": {"x": 2750, "y": 1029.0625},
            "pointsList": [
                {"x": 2567.520767922439, "y": 1060.5442998886515},
                {"x": 2667.520767922439, "y": 1060.5442998886515},
                {"x": 2650, "y": 1029.0625},
                {"x": 2750, "y": 1029.0625},
            ],
            "properties": {},
            "startPoint": {"x": 2567.520767922439, "y": 1060.5442998886515},
            "sourceNodeId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605",
            "targetNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "sourceAnchorId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605_right",
            "targetAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_left",
        },
        {
            "id": "56006748-d9fe-491b-a14b-04fd568cac08",
            "type": "app-edge",
            "endPoint": {"x": 3610, "y": 140.9375},
            "pointsList": [
                {"x": 3350, "y": 897.0625},
                {"x": 3450, "y": 897.0625},
                {"x": 3510, "y": 140.9375},
                {"x": 3610, "y": 140.9375},
            ],
            "properties": {},
            "startPoint": {"x": 3350, "y": 897.0625},
            "sourceNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "targetNodeId": "36a440a9-5b00-4d82-b13a-8e7819112918",
            "sourceAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_7887_right",
            "targetAnchorId": "36a440a9-5b00-4d82-b13a-8e7819112918_left",
        },
        {
            "id": "9bc8721b-07aa-4730-9347-910ed64e26b9",
            "type": "app-edge",
            "endPoint": {"x": 3610, "y": 1018.9375},
            "pointsList": [
                {"x": 3350, "y": 1023.0625},
                {"x": 3450, "y": 1023.0625},
                {"x": 3510, "y": 1018.9375},
                {"x": 3610, "y": 1018.9375},
            ],
            "properties": {},
            "startPoint": {"x": 3350, "y": 1023.0625},
            "sourceNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "targetNodeId": "f7c3b4a2-cb80-4e47-b050-7fef0315daaf",
            "sourceAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_6847_right",
            "targetAnchorId": "f7c3b4a2-cb80-4e47-b050-7fef0315daaf_left",
        },
        {
            "id": "e4b4bb4e-35ed-40a4-b4e7-b86f77131d92",
            "type": "app-edge",
            "endPoint": {"x": 540, "y": 1030.75},
            "pointsList": [
                {"x": 280, "y": 1008.125},
                {"x": 380, "y": 1008.125},
                {"x": 440, "y": 1030.75},
                {"x": 540, "y": 1030.75},
            ],
            "properties": {},
            "startPoint": {"x": 280, "y": 1008.125},
            "sourceNodeId": "start-node",
            "targetNodeId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "sourceAnchorId": "start-node_right",
            "targetAnchorId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94_left",
        },
        {
            "id": "0ea723ab-bebd-4058-98af-74b6c5f03260",
            "type": "app-edge",
            "endPoint": {"x": 1245.7315831103328, "y": 482.0191225666973},
            "pointsList": [
                {"x": 1140, "y": 961.75},
                {"x": 1240, "y": 961.75},
                {"x": 1145.7315831103328, "y": 482.0191225666973},
                {"x": 1245.7315831103328, "y": 482.0191225666973},
            ],
            "properties": {},
            "startPoint": {"x": 1140, "y": 961.75},
            "sourceNodeId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "targetNodeId": "a0089772-3821-474f-bb4f-9bfe32c1d95f",
            "sourceAnchorId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94_gWldyeZ3CMPKS9teLWQeI_right",
            "targetAnchorId": "a0089772-3821-474f-bb4f-9bfe32c1d95f_left",
        },
        {
            "id": "c0c675d3-cb0b-4b67-8009-16951303791d",
            "type": "app-edge",
            "endPoint": {"x": 1709.9423019523076, "y": 1073.1353016256758},
            "pointsList": [
                {"x": 1140, "y": 1052.75},
                {"x": 1240, "y": 1052.75},
                {"x": 1609.9423019523076, "y": 1073.1353016256758},
                {"x": 1709.9423019523076, "y": 1073.1353016256758},
            ],
            "properties": {},
            "startPoint": {"x": 1140, "y": 1052.75},
            "sourceNodeId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "targetNodeId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "sourceAnchorId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94_TvdY3NQkSdYbC8A15VrId_right",
            "targetAnchorId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836_left",
        },
        {
            "id": "0c1d5fc1-6ab2-431e-afdc-9f332ce8b466",
            "type": "app-edge",
            "endPoint": {"x": 1709.9423019523076, "y": 1073.1353016256758},
            "pointsList": [
                {"x": 1565.7315831103328, "y": 482.0191225666973},
                {"x": 1665.7315831103328, "y": 482.0191225666973},
                {"x": 1609.9423019523076, "y": 1073.1353016256758},
                {"x": 1709.9423019523076, "y": 1073.1353016256758},
            ],
            "properties": {},
            "startPoint": {"x": 1565.7315831103328, "y": 482.0191225666973},
            "sourceNodeId": "a0089772-3821-474f-bb4f-9bfe32c1d95f",
            "targetNodeId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "sourceAnchorId": "a0089772-3821-474f-bb4f-9bfe32c1d95f_right",
            "targetAnchorId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836_left",
        },
        {
            "id": "422564a4-2b0a-469b-be86-ded4204e7742",
            "type": "app-edge",
            "endPoint": {"x": 2247.520767922439, "y": 1060.5442998886515},
            "pointsList": [
                {"x": 2164.942301952309, "y": 1073.1353016256758},
                {"x": 2264.942301952309, "y": 1073.1353016256758},
                {"x": 2147.520767922439, "y": 1060.5442998886515},
                {"x": 2247.520767922439, "y": 1060.5442998886515},
            ],
            "properties": {},
            "startPoint": {"x": 2164.942301952309, "y": 1073.1353016256758},
            "sourceNodeId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "targetNodeId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605",
            "sourceAnchorId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836_right",
            "targetAnchorId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605_left",
        },
        {
            "id": "a0cee2ac-4d0d-4b68-8cb2-ca2cb39993e9",
            "type": "app-edge",
            "endPoint": {"x": 3470, "y": 1950},
            "pointsList": [
                {"x": 3350, "y": 1114.0625},
                {"x": 3450, "y": 1114.0625},
                {"x": 3370, "y": 1950},
                {"x": 3470, "y": 1950},
            ],
            "properties": {},
            "startPoint": {"x": 3350, "y": 1114.0625},
            "sourceNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "targetNodeId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "sourceAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_2794_right",
            "targetAnchorId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4_left",
        },
        {
            "id": "cd66759a-bcb9-4d61-806b-7bde23ae4582",
            "type": "app-edge",
            "endPoint": {"x": 4200, "y": 958.3125},
            "pointsList": [
                {"x": 4070, "y": 1881},
                {"x": 4170, "y": 1881},
                {"x": 4100, "y": 958.3125},
                {"x": 4200, "y": 958.3125},
            ],
            "properties": {},
            "startPoint": {"x": 4070, "y": 1881},
            "sourceNodeId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "targetNodeId": "dd02a0d8-0ea1-41c4-8b64-0cb7d8963fd9",
            "sourceAnchorId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4_Iu8b0BMQU9xXWy5JbcTnz_right",
            "targetAnchorId": "dd02a0d8-0ea1-41c4-8b64-0cb7d8963fd9_left",
        },
        {
            "id": "7113c5b7-d9d6-4f49-a030-24eaeee00e7d",
            "type": "app-edge",
            "endPoint": {"x": 4200, "y": 1955.0625},
            "pointsList": [
                {"x": 4070, "y": 1972},
                {"x": 4170, "y": 1972},
                {"x": 4100, "y": 1955.0625},
                {"x": 4200, "y": 1955.0625},
            ],
            "properties": {},
            "startPoint": {"x": 4070, "y": 1972},
            "sourceNodeId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "targetNodeId": "04dd6c1e-95f9-4757-bb3e-134d503fce54",
            "sourceAnchorId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4_s-groW06vt6a7B-aqDqnX_right",
            "targetAnchorId": "04dd6c1e-95f9-4757-bb3e-134d503fce54_left",
        },
    ],
    "nodes": [
        {
            "x": 120,
            "y": 47.25,
            "id": "base-node",
            "type": "base-node",
            "properties": {
                "width": 600,
                "config": {},
                "height": 838.75,
                "showNode": True,
                "stepName": "基本信息",
                "node_data": {
                    "desc": "www",
                    "name": "www",
                    "prologue": "",
                    "tts_type": "BROWSER",
                    "stt_autosend": False,
                    "stt_model_id": "",
                    "tts_autoplay": False,
                    "tts_model_id": "",
                    "long_term_enable": False,
                    "stt_model_enable": False,
                    "tts_model_enable": False,
                    "stt_model_id_type": "default",
                    "file_upload_enable": False,
                    "long_term_model_id": "",
                    "file_upload_setting": {
                        "audio": False,
                        "image": False,
                        "other": False,
                        "video": False,
                        "document": True,
                        "maxFiles": 3,
                        "fileLimit": 50,
                        "url_upload": False,
                        "local_upload": True,
                        "otherExtensions": ["PPT", "DOC"],
                    },
                    "long_term_trigger_type": "ROUND",
                    "long_term_model_id_type": "default",
                    "stt_model_params_setting": {},
                    "tts_model_params_setting": {},
                    "long_term_trigger_setting": {"rounds": 10},
                    "long_term_model_params_setting": {},
                },
                "enableException": False,
                "input_field_list": [],
                "user_input_config": {"title": "用户输入"},
                "api_input_field_list": [],
                "chat_input_field_list": [],
                "user_input_field_list": [
                    {
                        "attrs": {},
                        "field": "problem_optimization",
                        "label": {
                            "attrs": {"tooltip": "是否需要问题优化"},
                            "label": "问题优化",
                            "input_type": "TooltipLabel",
                            "props_info": {},
                        },
                        "required": True,
                        "input_type": "SwitchInput",
                        "default_value": False,
                        "visibility_rules": {
                            "action": "show",
                            "node_id": "base-node",
                            "condition": "and",
                            "node_name": "基本信息",
                            "conditions": [],
                        },
                        "show_default_value": True,
                    },
                    {
                        "attrs": {},
                        "field": "ai_questioning",
                        "label": {
                            "attrs": {"tooltip": "是否ai回复"},
                            "label": "是否ai回复",
                            "input_type": "TooltipLabel",
                            "props_info": {},
                        },
                        "required": True,
                        "input_type": "SwitchInput",
                        "default_value": False,
                        "visibility_rules": {
                            "action": "show",
                            "node_id": "base-node",
                            "condition": "and",
                            "node_name": "基本信息",
                            "conditions": [],
                        },
                        "show_default_value": True,
                    },
                ],
            },
        },
        {
            "x": 120,
            "y": 1008.125,
            "id": "start-node",
            "type": "start-node",
            "properties": {
                "width": 320,
                "config": {
                    "fields": [{"label": "用户问题", "value": "question"}],
                    "chatFields": [],
                    "globalFields": [
                        {"label": "当前时间", "value": "time"},
                        {"label": "历史聊天记录", "value": "history_context"},
                        {"label": "对话 ID", "value": "chat_id"},
                        {"label": "对话用户 ID", "value": "chat_user_id"},
                        {"label": "对话用户类型", "value": "chat_user_type"},
                        {"label": "对话用户组", "value": "chat_user_group"},
                        {"label": "对话用户", "value": "chat_user"},
                        {"label": "问题优化", "value": "problem_optimization"},
                        {"label": "是否ai回复", "value": "ai_questioning"},
                    ],
                },
                "fields": [{"label": "用户问题", "value": "question"}],
                "height": 552,
                "showNode": True,
                "stepName": "开始",
                "globalFields": [{"label": "当前时间", "value": "time"}],
                "enableException": False,
            },
        },
        {
            "x": 2407.520767922439,
            "y": 1060.5442998886515,
            "id": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605",
            "type": "search-knowledge-node",
            "properties": {
                "width": 320,
                "config": {
                    "fields": [
                        {"label": "检索结果的分段列表", "value": "paragraph_list"},
                        {"label": "满足直接回答的分段列表", "value": "is_hit_handling_method_list"},
                        {"label": "检索结果", "value": "data"},
                        {"label": "满足直接回答的分段内容", "value": "directly_return"},
                    ]
                },
                "height": 816,
                "showNode": True,
                "stepName": "知识库检索",
                "condition": "AND",
                "node_data": {
                    "image_list": [],
                    "knowledge_list": [],
                    "show_knowledge": True,
                    "knowledge_id_list": [],
                    "knowledge_setting": {
                        "top_n": 3,
                        "similarity": 0.6,
                        "search_mode": "embedding",
                        "max_paragraph_char_number": 5000,
                    },
                    "search_scope_type": "custom",
                    "search_scope_source": "knowledge",
                    "all_knowledge_id_list": [],
                    "search_scope_reference": [],
                    "question_reference_address": ["124fe8a0-70fa-42cb-b854-4b6c02ebb836", "Group1"],
                    "no_permission_knowledge_id_list": [],
                },
                "enableException": False,
            },
        },
        {
            "x": 3050,
            "y": 1029.0625,
            "id": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "type": "condition-node",
            "properties": {
                "width": 600,
                "config": {"fields": [{"label": "分支名称", "value": "branch_name"}]},
                "height": 502,
                "showNode": True,
                "stepName": "判断器",
                "condition": "AND",
                "node_data": {
                    "branch": [
                        {
                            "id": "7887",
                            "type": "IF",
                            "condition": "and",
                            "conditions": [
                                {
                                    "field": ["fd0324fc-f5e4-4fa6-a2d9-cb251b467605", "is_hit_handling_method_list"],
                                    "value": 1,
                                    "compare": "is_not_null",
                                }
                            ],
                        },
                        {
                            "id": "6847",
                            "type": "ELSE IF 1",
                            "condition": "and",
                            "conditions": [
                                {
                                    "field": ["fd0324fc-f5e4-4fa6-a2d9-cb251b467605", "paragraph_list"],
                                    "value": 1,
                                    "compare": "is_not_null",
                                }
                            ],
                        },
                        {"id": "2794", "type": "ELSE", "condition": "and", "conditions": []},
                    ]
                },
                "enableException": False,
                "branch_condition_list": [
                    {"id": "7887", "index": 0, "height": 118},
                    {"id": "6847", "index": 1, "height": 118},
                    {"id": "2794", "index": 2, "height": 48},
                ],
            },
        },
        {
            "x": 3770,
            "y": 140.9375,
            "id": "36a440a9-5b00-4d82-b13a-8e7819112918",
            "type": "reply-node",
            "properties": {
                "width": 320,
                "config": {"fields": [{"label": "内容", "value": "answer"}]},
                "height": 377.375,
                "showNode": True,
                "stepName": "指定回复",
                "condition": "AND",
                "node_data": {
                    "fields": ["fd0324fc-f5e4-4fa6-a2d9-cb251b467605", "directly_return"],
                    "content": "",
                    "is_result": True,
                    "reply_type": "referencing",
                    "content_type": "TEXT",
                },
                "enableException": False,
            },
        },
        {
            "x": 3770,
            "y": 1018.9375,
            "id": "f7c3b4a2-cb80-4e47-b050-7fef0315daaf",
            "type": "ai-chat-node",
            "properties": {
                "width": 320,
                "config": {
                    "fields": [
                        {"label": "AI 回答内容", "value": "answer"},
                        {"label": "思考过程", "value": "reasoning_content"},
                        {"label": "历史聊天记录", "value": "history_message"},
                    ]
                },
                "height": 1105.375,
                "showNode": True,
                "stepName": "AI 对话",
                "condition": "AND",
                "node_data": {
                    "prompt": "",
                    "system": "",
                    "vision": False,
                    "model_id": "",
                    "tool_ids": [],
                    "is_result": True,
                    "image_list": [],
                    "max_tokens": None,
                    "mcp_source": "referencing",
                    "video_list": [],
                    "mcp_servers": "",
                    "temperature": None,
                    "mcp_tool_ids": [],
                    "dialogue_type": "WORKFLOW",
                    "model_id_type": "custom",
                    "model_setting": {
                        "reasoning_content_end": "</think>",
                        "reasoning_content_start": "<think>",
                        "reasoning_content_enable": False,
                    },
                    "skill_tool_ids": [],
                    "application_ids": [],
                    "dialogue_number": 1,
                    "mcp_output_enable": True,
                    "model_id_reference": [],
                    "model_params_setting": {},
                },
                "enableException": False,
            },
        },
        {
            "x": 4360,
            "y": 1955.0625,
            "id": "04dd6c1e-95f9-4757-bb3e-134d503fce54",
            "type": "reply-node",
            "properties": {
                "width": 320,
                "config": {"fields": [{"label": "内容", "value": "answer"}]},
                "height": 475.375,
                "showNode": True,
                "stepName": "指定回复1",
                "condition": "AND",
                "node_data": {
                    "fields": [],
                    "content": "抱歉，没有在知识库查询到相关内容，请提供更详细的信息。",
                    "is_result": True,
                    "reply_type": "content",
                    "content_type": "TEXT",
                },
                "enableException": False,
            },
        },
        {
            "x": 840,
            "y": 1030.75,
            "id": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "type": "condition-node",
            "properties": {
                "width": 600,
                "config": {"fields": [{"label": "分支名称", "value": "branch_name"}]},
                "height": 376,
                "showNode": True,
                "stepName": "判断器1",
                "condition": "AND",
                "node_data": {
                    "branch": [
                        {
                            "id": "gWldyeZ3CMPKS9teLWQeI",
                            "type": "IF",
                            "condition": "and",
                            "conditions": [
                                {"field": ["global", "problem_optimization"], "value": 1, "compare": "is_true"}
                            ],
                        },
                        {"id": "TvdY3NQkSdYbC8A15VrId", "type": "ELSE", "condition": "and", "conditions": []},
                    ]
                },
                "enableException": False,
                "branch_condition_list": [
                    {"id": "gWldyeZ3CMPKS9teLWQeI", "index": 0, "height": 118},
                    {"id": "TvdY3NQkSdYbC8A15VrId", "index": 1, "height": 48},
                ],
            },
        },
        {
            "x": 1405.7315831103328,
            "y": 482.0191225666973,
            "id": "a0089772-3821-474f-bb4f-9bfe32c1d95f",
            "type": "question-node",
            "properties": {
                "width": 320,
                "config": {"fields": [{"label": "问题优化结果", "value": "answer"}]},
                "height": 761.375,
                "showNode": True,
                "stepName": "问题优化",
                "condition": "AND",
                "node_data": {
                    "prompt": "{{开始.question}}",
                    "system": "# 角色\n你是一位问题优化大师，擅长根据上下文精准揣测用户意图，并对用户提出的问题进行优化。\n## 技能\n### 技能 1: 优化问题\n2. 接收用户输入的问题。\n3. 依据上下文仔细分析问题含义。\n4. 输出优化后的问题。\n\n## 限制:\n- 仅返回优化后的问题，不进行额外解释或说明。\n- 确保优化后的问题准确反映原始问题意图，不得改变原意。",
                    "model_id": "",
                    "is_result": False,
                    "dialogue_type": "NODE",
                    "model_id_type": "default",
                    "dialogue_number": 0,
                    "model_id_reference": [],
                    "model_params_setting": {},
                },
                "enableException": False,
            },
        },
        {
            "x": 1937.4423019523076,
            "y": 1073.1353016256758,
            "id": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "type": "variable-aggregation-node",
            "properties": {
                "width": 455,
                "config": {"fields": [{"label": "Group1", "value": "Group1"}]},
                "height": 492,
                "showNode": True,
                "stepName": "变量聚合",
                "condition": "OR",
                "node_data": {
                    "strategy": "first_non_null",
                    "is_result": True,
                    "group_list": [
                        {
                            "id": "A5aBuBrQJ5hq12mKSJNiQ",
                            "field": "Group1",
                            "label": "Group1",
                            "variable_list": [
                                {
                                    "v_id": "0bmeMSbo9696jwbfp3jDX",
                                    "variable": ["a0089772-3821-474f-bb4f-9bfe32c1d95f", "answer"],
                                },
                                {"v_id": "1YHRj-fr3_IQpELv_HAdC", "variable": ["start-node", "question"]},
                            ],
                        }
                    ],
                },
                "enableException": False,
            },
        },
        {
            "x": 4360,
            "y": 958.3125,
            "id": "dd02a0d8-0ea1-41c4-8b64-0cb7d8963fd9",
            "type": "ai-chat-node",
            "properties": {
                "width": 320,
                "config": {
                    "fields": [
                        {"label": "AI 回答内容", "value": "answer"},
                        {"label": "思考过程", "value": "reasoning_content"},
                        {"label": "历史聊天记录", "value": "history_message"},
                    ]
                },
                "height": 1105.375,
                "showNode": True,
                "stepName": "AI 对话1",
                "condition": "AND",
                "node_data": {
                    "prompt": "{{开始.question}}",
                    "system": "",
                    "vision": False,
                    "model_id": "",
                    "tool_ids": [],
                    "is_result": True,
                    "image_list": [],
                    "max_tokens": None,
                    "mcp_source": "referencing",
                    "video_list": [],
                    "mcp_servers": "",
                    "temperature": None,
                    "mcp_tool_ids": [],
                    "dialogue_type": "WORKFLOW",
                    "model_id_type": "custom",
                    "model_setting": {
                        "reasoning_content_end": "</think>",
                        "reasoning_content_start": "<think>",
                        "reasoning_content_enable": False,
                    },
                    "skill_tool_ids": [],
                    "application_ids": [],
                    "dialogue_number": 0,
                    "mcp_output_enable": True,
                    "model_id_reference": [],
                    "model_params_setting": {},
                },
                "enableException": False,
            },
        },
        {
            "x": 3770,
            "y": 1950,
            "id": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "type": "condition-node",
            "properties": {
                "width": 600,
                "config": {"fields": [{"label": "分支名称", "value": "branch_name"}]},
                "height": 376,
                "showNode": True,
                "stepName": "判断器2",
                "condition": "AND",
                "node_data": {
                    "branch": [
                        {
                            "id": "Iu8b0BMQU9xXWy5JbcTnz",
                            "type": "IF",
                            "condition": "and",
                            "conditions": [{"field": ["global", "ai_questioning"], "value": 1, "compare": "is_true"}],
                        },
                        {"id": "s-groW06vt6a7B-aqDqnX", "type": "ELSE", "condition": "and", "conditions": []},
                    ]
                },
                "enableException": False,
                "branch_condition_list": [
                    {"id": "Iu8b0BMQU9xXWy5JbcTnz", "index": 0, "height": 118},
                    {"id": "s-groW06vt6a7B-aqDqnX", "index": 1, "height": 48},
                ],
            },
        },
    ],
}


def build_workflow(application):
    from application.models import ApplicationVersion
    from system_manage.models.resource_mapping import ResourceMapping, ResourceType

    # 深拷贝模板，避免修改模块级模板导致请求之间串配置
    data = copy.deepcopy(template)
    knowledge_setting = application.knowledge_setting or {}
    no_references_setting = knowledge_setting.get("no_references_setting") or {}
    model_setting = application.model_setting or {}
    # 发布版本使用发布时的知识库快照；调试使用 Application 本体，从资源映射读取
    if isinstance(application, ApplicationVersion):
        knowledge_ids = application.knowledge_ids
    else:
        knowledge_ids = [
            str(target_id)
            for target_id in QuerySet(ResourceMapping)
            .filter(source_type=ResourceType.APPLICATION, source_id=application.id, target_type=ResourceType.KNOWLEDGE)
            .values_list("target_id", flat=True)
        ]

    data["nodes"][0]["properties"]["user_input_field_list"][0]["default_value"] = application.problem_optimization

    data["nodes"][0]["properties"]["user_input_field_list"][1]["default_value"] = (
        no_references_setting.get("status") == "ai_questioning"
    )
    # Application 的外键与 ApplicationVersion 的字段都提供 model_id
    model_id = str(application.model_id) if application.model_id else ""
    model_params_setting = application.model_params_setting or {}
    ## 问题优化设置
    data["nodes"][8]["properties"]["node_data"]["model_id"] = model_id
    data["nodes"][8]["properties"]["node_data"]["prompt"] = application.problem_optimization_prompt.replace(
        "{question}", "{{开始.question}}"
    )
    data["nodes"][8]["properties"]["node_data"]["model_params_setting"] = model_params_setting
    ## 知识库检索
    data["nodes"][2]["properties"]["node_data"]["knowledge_id_list"] = knowledge_ids
    data["nodes"][2]["properties"]["node_data"]["knowledge_setting"] = knowledge_setting
    ## ai对话
    data["nodes"][5]["properties"]["node_data"]["model_id"] = model_id
    data["nodes"][5]["properties"]["node_data"]["model_params_setting"] = model_params_setting
    data["nodes"][5]["properties"]["node_data"]["prompt"] = (
        (model_setting.get("prompt") or "")
        .replace("{question}", "{{开始.question}}")
        .replace("{data}", "{{知识库检索.data}}")
    )
    data["nodes"][5]["properties"]["node_data"]["system"] = model_setting.get("system")
    data["nodes"][5]["properties"]["node_data"]["mcp_tool_ids"] = application.mcp_tool_ids
    data["nodes"][5]["properties"]["node_data"]["mcp_servers"] = application.mcp_servers
    data["nodes"][5]["properties"]["node_data"]["application_ids"] = application.application_ids
    data["nodes"][5]["properties"]["node_data"]["tool_ids"] = application.tool_ids
    ## 未查询到知识库ai 回复
    data["nodes"][10]["properties"]["node_data"]["model_id"] = model_id
    data["nodes"][10]["properties"]["node_data"]["model_params_setting"] = model_params_setting
    data["nodes"][10]["properties"]["node_data"]["prompt"] = model_setting.get("no_references_prompt").replace(
        "{question}", "{{开始.question}}"
    )
    data["nodes"][10]["properties"]["node_data"]["mcp_tool_ids"] = application.mcp_tool_ids
    data["nodes"][10]["properties"]["node_data"]["mcp_servers"] = application.mcp_servers
    data["nodes"][10]["properties"]["node_data"]["application_ids"] = application.application_ids
    data["nodes"][10]["properties"]["node_data"]["tool_ids"] = application.tool_ids
    ## 未查询到知识库指定回复
    if no_references_setting.get("status") == "designated_answer":
        data["nodes"][6]["properties"]["node_data"]["content"] = no_references_setting.get("value")

    return data
