from django.db.models import QuerySet

template = {
    "edges": [
        {
            "id": "6a8d23d9-5179-424e-80c2-f08d37cdb8d4",
            "type": "app-edge",
            "endPoint": {"x": 2760, "y": 1054.125},
            "pointsList": [
                {"x": 2620, "y": 1054.125},
                {"x": 2730, "y": 1054.125},
                {"x": 2650, "y": 1054.125},
                {"x": 2760, "y": 1054.125},
            ],
            "properties": {},
            "startPoint": {"x": 2620, "y": 1054.125},
            "sourceNodeId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605",
            "targetNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "sourceAnchorId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605_right",
            "targetAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_left",
        },
        {
            "id": "56006748-d9fe-491b-a14b-04fd568cac08",
            "type": "app-edge",
            "endPoint": {"x": 3610, "y": 149.25},
            "pointsList": [
                {"x": 3340, "y": 913.75},
                {"x": 3450, "y": 913.75},
                {"x": 3500, "y": 149.25},
                {"x": 3610, "y": 149.25},
            ],
            "properties": {},
            "startPoint": {"x": 3340, "y": 913.75},
            "sourceNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "targetNodeId": "36a440a9-5b00-4d82-b13a-8e7819112918",
            "sourceAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_7887_right",
            "targetAnchorId": "36a440a9-5b00-4d82-b13a-8e7819112918_left",
        },
        {
            "id": "9bc8721b-07aa-4730-9347-910ed64e26b9",
            "type": "app-edge",
            "endPoint": {"x": 3610, "y": 1054.125},
            "pointsList": [
                {"x": 3340, "y": 1043.125},
                {"x": 3450, "y": 1043.125},
                {"x": 3500, "y": 1054.125},
                {"x": 3610, "y": 1054.125},
            ],
            "properties": {},
            "startPoint": {"x": 3340, "y": 1043.125},
            "sourceNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "targetNodeId": "f7c3b4a2-cb80-4e47-b050-7fef0315daaf",
            "sourceAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_6847_right",
            "targetAnchorId": "f7c3b4a2-cb80-4e47-b050-7fef0315daaf_left",
        },
        {
            "id": "e4b4bb4e-35ed-40a4-b4e7-b86f77131d92",
            "type": "app-edge",
            "endPoint": {"x": 550, "y": 1054.125},
            "pointsList": [
                {"x": 280, "y": 1054.125},
                {"x": 390, "y": 1054.125},
                {"x": 440, "y": 1054.125},
                {"x": 550, "y": 1054.125},
            ],
            "properties": {},
            "startPoint": {"x": 280, "y": 1054.125},
            "sourceNodeId": "start-node",
            "targetNodeId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "sourceAnchorId": "start-node_right",
            "targetAnchorId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94_left",
        },
        {
            "id": "0ea723ab-bebd-4058-98af-74b6c5f03260",
            "type": "app-edge",
            "endPoint": {"x": 1270, "y": 1054.125},
            "pointsList": [
                {"x": 1130, "y": 978.4375},
                {"x": 1240, "y": 978.4375},
                {"x": 1160, "y": 1054.125},
                {"x": 1270, "y": 1054.125},
            ],
            "properties": {},
            "startPoint": {"x": 1130, "y": 978.4375},
            "sourceNodeId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "targetNodeId": "a0089772-3821-474f-bb4f-9bfe32c1d95f",
            "sourceAnchorId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94_gWldyeZ3CMPKS9teLWQeI_right",
            "targetAnchorId": "a0089772-3821-474f-bb4f-9bfe32c1d95f_left",
        },
        {
            "id": "c0c675d3-cb0b-4b67-8009-16951303791d",
            "type": "app-edge",
            "endPoint": {"x": 1730, "y": 1054.125},
            "pointsList": [
                {"x": 1130, "y": 1069.125},
                {"x": 1240, "y": 1069.125},
                {"x": 1620, "y": 1054.125},
                {"x": 1730, "y": 1054.125},
            ],
            "properties": {},
            "startPoint": {"x": 1130, "y": 1069.125},
            "sourceNodeId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "targetNodeId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "sourceAnchorId": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94_TvdY3NQkSdYbC8A15VrId_right",
            "targetAnchorId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836_left",
        },
        {
            "id": "0c1d5fc1-6ab2-431e-afdc-9f332ce8b466",
            "type": "app-edge",
            "endPoint": {"x": 1730, "y": 1054.125},
            "pointsList": [
                {"x": 1590, "y": 1054.125},
                {"x": 1700, "y": 1054.125},
                {"x": 1620, "y": 1054.125},
                {"x": 1730, "y": 1054.125},
            ],
            "properties": {},
            "startPoint": {"x": 1590, "y": 1054.125},
            "sourceNodeId": "a0089772-3821-474f-bb4f-9bfe32c1d95f",
            "targetNodeId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "sourceAnchorId": "a0089772-3821-474f-bb4f-9bfe32c1d95f_right",
            "targetAnchorId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836_left",
        },
        {
            "id": "422564a4-2b0a-469b-be86-ded4204e7742",
            "type": "app-edge",
            "endPoint": {"x": 2300, "y": 1054.125},
            "pointsList": [
                {"x": 2160, "y": 1054.125},
                {"x": 2270, "y": 1054.125},
                {"x": 2190, "y": 1054.125},
                {"x": 2300, "y": 1054.125},
            ],
            "properties": {},
            "startPoint": {"x": 2160, "y": 1054.125},
            "sourceNodeId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "targetNodeId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605",
            "sourceAnchorId": "124fe8a0-70fa-42cb-b854-4b6c02ebb836_right",
            "targetAnchorId": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605_left",
        },
        {
            "id": "a0cee2ac-4d0d-4b68-8cb2-ca2cb39993e9",
            "type": "app-edge",
            "endPoint": {"x": 3480, "y": 1973.375},
            "pointsList": [
                {"x": 3340, "y": 1133.8125},
                {"x": 3450, "y": 1133.8125},
                {"x": 3370, "y": 1973.375},
                {"x": 3480, "y": 1973.375},
            ],
            "properties": {},
            "startPoint": {"x": 3340, "y": 1133.8125},
            "sourceNodeId": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "targetNodeId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "sourceAnchorId": "420a6e4f-44ff-4847-bb81-0923630846b5_2794_right",
            "targetAnchorId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4_left",
        },
        {
            "id": "cd66759a-bcb9-4d61-806b-7bde23ae4582",
            "type": "app-edge",
            "endPoint": {"x": 4200, "y": 1001.5},
            "pointsList": [
                {"x": 4060, "y": 1897.6875},
                {"x": 4170, "y": 1897.6875},
                {"x": 4090, "y": 1001.5},
                {"x": 4200, "y": 1001.5},
            ],
            "properties": {},
            "startPoint": {"x": 4060, "y": 1897.6875},
            "sourceNodeId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "targetNodeId": "dd02a0d8-0ea1-41c4-8b64-0cb7d8963fd9",
            "sourceAnchorId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4_Iu8b0BMQU9xXWy5JbcTnz_right",
            "targetAnchorId": "dd02a0d8-0ea1-41c4-8b64-0cb7d8963fd9_left",
        },
        {
            "id": "7113c5b7-d9d6-4f49-a030-24eaeee00e7d",
            "type": "app-edge",
            "endPoint": {"x": 4200, "y": 1973.375},
            "pointsList": [
                {"x": 4060, "y": 1988.375},
                {"x": 4170, "y": 1988.375},
                {"x": 4090, "y": 1973.375},
                {"x": 4200, "y": 1973.375},
            ],
            "properties": {},
            "startPoint": {"x": 4060, "y": 1988.375},
            "sourceNodeId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "targetNodeId": "04dd6c1e-95f9-4757-bb3e-134d503fce54",
            "sourceAnchorId": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4_s-groW06vt6a7B-aqDqnX_right",
            "targetAnchorId": "04dd6c1e-95f9-4757-bb3e-134d503fce54_left",
        },
    ],
    "nodes": [
        {
            "x": 120,
            "y": 120,
            "id": "base-node",
            "type": "base-node",
            "properties": {
                "config": {},
                "height": 984.25,
                "showNode": True,
                "stepName": "基本信息",
                "node_data": {
                    "desc": "www",
                    "name": "www",
                    "prologue": "您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务",
                    "tts_type": "BROWSER",
                    "stt_model_id_type": "default",
                    "long_term_model_id_type": "default",
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
            "y": 1054.125,
            "id": "start-node",
            "type": "start-node",
            "properties": {
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
                "height": 644,
                "showNode": True,
                "stepName": "开始",
                "globalFields": [{"label": "当前时间", "value": "time"}],
                "enableException": False,
            },
        },
        {
            "x": 2460,
            "y": 1054.125,
            "id": "fd0324fc-f5e4-4fa6-a2d9-cb251b467605",
            "type": "search-knowledge-node",
            "properties": {
                "config": {
                    "fields": [
                        {"label": "检索结果的分段列表", "value": "paragraph_list"},
                        {"label": "满足直接回答的分段列表", "value": "is_hit_handling_method_list"},
                        {"label": "检索结果", "value": "data"},
                        {"label": "满足直接回答的分段内容", "value": "directly_return"},
                    ]
                },
                "height": 806.375,
                "showNode": True,
                "stepName": "知识库检索",
                "condition": "AND",
                "node_data": {
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
                    "question_reference_address": ["124fe8a0-70fa-42cb-b854-4b6c02ebb836", "Group1"],
                    "no_permission_knowledge_id_list": [],
                },
                "enableException": False,
            },
        },
        {
            "x": 3050,
            "y": 1054.125,
            "id": "420a6e4f-44ff-4847-bb81-0923630846b5",
            "type": "condition-node",
            "properties": {
                "width": 600,
                "config": {"fields": [{"label": "分支名称", "value": "branch_name"}]},
                "height": 552.125,
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
                                    "compare": "is_not_None",
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
                                    "compare": "is_not_None",
                                }
                            ],
                        },
                        {"id": "2794", "type": "ELSE", "condition": "and", "conditions": []},
                    ]
                },
                "enableException": False,
                "branch_condition_list": [
                    {"id": "7887", "index": 0, "height": 121.375},
                    {"id": "6847", "index": 1, "height": 121.375},
                    {"id": "2794", "index": 2, "height": 44},
                ],
            },
        },
        {
            "x": 3770,
            "y": 149.25,
            "id": "36a440a9-5b00-4d82-b13a-8e7819112918",
            "type": "reply-node",
            "properties": {
                "config": {"fields": [{"label": "内容", "value": "answer"}]},
                "height": 394,
                "showNode": True,
                "stepName": "指定回复",
                "condition": "AND",
                "node_data": {
                    "fields": ["fd0324fc-f5e4-4fa6-a2d9-cb251b467605", "directly_return"],
                    "content": "",
                    "is_result": True,
                    "reply_type": "referencing",
                },
                "enableException": False,
            },
        },
        {
            "x": 3770,
            "y": 1054.125,
            "id": "f7c3b4a2-cb80-4e47-b050-7fef0315daaf",
            "type": "ai-chat-node",
            "properties": {
                "config": {
                    "fields": [
                        {"label": "AI 回答内容", "value": "answer"},
                        {"label": "思考过程", "value": "reasoning_content"},
                        {"label": "历史聊天记录", "value": "history_message"},
                    ]
                },
                "height": 1175.75,
                "showNode": True,
                "stepName": "AI 对话",
                "condition": "AND",
                "node_data": {
                    "prompt": "已知信息：\n{{知识库检索.data}}\n问题：\n{{开始.question}}",
                    "system": "",
                    "model_id": "",
                    "is_result": True,
                    "max_tokens": None,
                    "temperature": None,
                    "dialogue_type": "WORKFLOW",
                    "model_id_type": "custom",
                    "model_setting": {
                        "reasoning_content_end": "</think>",
                        "reasoning_content_start": "<think>",
                        "reasoning_content_enable": False,
                    },
                    "dialogue_number": 1,
                    "mcp_output_enable": True,
                    "model_id_reference": [],
                },
                "enableException": False,
            },
        },
        {
            "x": 4360,
            "y": 1973.375,
            "id": "04dd6c1e-95f9-4757-bb3e-134d503fce54",
            "type": "reply-node",
            "properties": {
                "config": {"fields": [{"label": "内容", "value": "answer"}]},
                "height": 512,
                "showNode": True,
                "stepName": "指定回复1",
                "condition": "AND",
                "node_data": {
                    "fields": [],
                    "content": "抱歉，没有在知识库查询到相关内容，请提供更详细的信息。",
                    "is_result": True,
                    "reply_type": "content",
                },
                "enableException": False,
            },
        },
        {
            "x": 840,
            "y": 1054.125,
            "id": "b4dd9d45-25f0-4b01-9ec3-557a46a97d94",
            "type": "condition-node",
            "properties": {
                "width": 600,
                "config": {"fields": [{"label": "分支名称", "value": "branch_name"}]},
                "height": 422.75,
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
                                {"field": ["global", "problem_optimization"], "value": 1, "compare": "is_True"}
                            ],
                        },
                        {"id": "TvdY3NQkSdYbC8A15VrId", "type": "ELSE", "condition": "and", "conditions": []},
                    ]
                },
                "enableException": False,
                "branch_condition_list": [
                    {"id": "gWldyeZ3CMPKS9teLWQeI", "index": 0, "height": 121.375},
                    {"id": "TvdY3NQkSdYbC8A15VrId", "index": 1, "height": 44},
                ],
            },
        },
        {
            "x": 1430,
            "y": 1054.125,
            "id": "a0089772-3821-474f-bb4f-9bfe32c1d95f",
            "type": "question-node",
            "properties": {
                "config": {"fields": [{"label": "问题优化结果", "value": "answer"}]},
                "height": 842,
                "showNode": True,
                "stepName": "问题优化",
                "condition": "AND",
                "node_data": {
                    "prompt": "{{开始.question}}",
                    "system": "# 角色\n你是一位问题优化大师，擅长根据上下文精准揣测用户意图，并对用户提出的问题进行优化。\n\n## 技能\n### 技能 1: 优化问题\n2. 接收用户输入的问题。\n3. 依据上下文仔细分析问题含义。\n4. 输出优化后的问题。\n\n## 限制:\n- 仅返回优化后的问题，不进行额外解释或说明。\n- 确保优化后的问题准确反映原始问题意图，不得改变原意。",
                    "model_id": "",
                    "is_result": False,
                    "model_id_type": "default",
                    "dialogue_number": 0,
                    "model_id_reference": [],
                },
                "enableException": False,
            },
        },
        {
            "x": 1945,
            "y": 1054.125,
            "id": "124fe8a0-70fa-42cb-b854-4b6c02ebb836",
            "type": "variable-aggregation-node",
            "properties": {
                "config": {"fields": [{"label": "Group1", "value": "Group1"}]},
                "height": 530.75,
                "showNode": True,
                "stepName": "变量聚合",
                "condition": "AND",
                "node_data": {
                    "strategy": "first_non_None",
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
            "y": 1001.5,
            "id": "dd02a0d8-0ea1-41c4-8b64-0cb7d8963fd9",
            "type": "ai-chat-node",
            "properties": {
                "config": {
                    "fields": [
                        {"label": "AI 回答内容", "value": "answer"},
                        {"label": "思考过程", "value": "reasoning_content"},
                        {"label": "历史聊天记录", "value": "history_message"},
                    ]
                },
                "height": 1191.75,
                "showNode": True,
                "stepName": "AI 对话1",
                "condition": "AND",
                "node_data": {
                    "prompt": "{{开始.question}}",
                    "system": "",
                    "model_id": "",
                    "is_result": True,
                    "max_tokens": None,
                    "temperature": None,
                    "dialogue_type": "WORKFLOW",
                    "model_id_type": "custom",
                    "model_setting": {
                        "reasoning_content_end": "</think>",
                        "reasoning_content_start": "<think>",
                        "reasoning_content_enable": False,
                    },
                    "dialogue_number": 0,
                    "mcp_output_enable": True,
                    "model_id_reference": [],
                },
                "enableException": False,
            },
        },
        {
            "x": 3770,
            "y": 1973.375,
            "id": "f9ae6300-5b07-4244-9b88-2a5e7329e1d4",
            "type": "condition-node",
            "properties": {
                "width": 600,
                "config": {"fields": [{"label": "分支名称", "value": "branch_name"}]},
                "height": 422.75,
                "showNode": True,
                "stepName": "判断器2",
                "condition": "AND",
                "node_data": {
                    "branch": [
                        {
                            "id": "Iu8b0BMQU9xXWy5JbcTnz",
                            "type": "IF",
                            "condition": "and",
                            "conditions": [{"field": ["global", "ai_questioning"], "value": 1, "compare": "is_True"}],
                        },
                        {"id": "s-groW06vt6a7B-aqDqnX", "type": "ELSE", "condition": "and", "conditions": []},
                    ]
                },
                "enableException": False,
                "branch_condition_list": [
                    {"id": "Iu8b0BMQU9xXWy5JbcTnz", "index": 0, "height": 121.375},
                    {"id": "s-groW06vt6a7B-aqDqnX", "index": 1, "height": 44},
                ],
            },
        },
    ],
}


def build_workflow(application):
    from system_manage.models.resource_mapping import ResourceMapping, ResourceType

    data = template.copy()
    if application.knowledge_ids:
        knowledge_ids = application.knowledge_ids
    else:
        knowledge_ids = (
            QuerySet(ResourceMapping)
            .filter(source_type=ResourceType.APPLICATION, source_id=application.id, target_type=ResourceType.KNOWLEDGE)
            .values_list("target_id", flat=True)
        )

    data["nodes"][0]["properties"]["user_input_field_list"][0]["default_value"] = application.problem_optimization

    data["nodes"][0]["properties"]["user_input_field_list"][1]["default_value"] = (
        application.knowledge_setting.no_references_setting.status == "ai_questioning"
    )
    model_id = application.model
    model_params_setting = application.model_params_setting or {}
    ## 问题优化设置
    data["nodes"][8]["properties"]["node_data"]["model_id"] = model_id
    data["nodes"][8]["properties"]["node_data"]["prompt"] = application.problem_optimization_prompt.replace(
        "{question}", "{{开始.question}}"
    )
    data["nodes"][8]["properties"]["node_data"]["model_params_setting"] = model_params_setting
    ## 知识库检索
    data["nodes"][2]["properties"]["node_data"]["knowledge_id_list"] = knowledge_ids
    data["nodes"][2]["properties"]["node_data"]["knowledge_setting"] = application.knowledge_setting
    ## ai对话
    data["nodes"][5]["properties"]["node_data"]["model_id"] = model_id
    data["nodes"][5]["properties"]["node_data"]["model_params_setting"] = model_params_setting
    data["nodes"][5]["properties"]["node_data"]["prompt"] = application.model_setting.prompt
    ## 未查询到知识库ai 回复
    data["nodes"][10]["properties"]["node_data"]["model_id"] = model_id
    data["nodes"][10]["properties"]["node_data"]["model_params_setting"] = model_params_setting
    ## 未查询到知识库指定回复
    if application.knowledge_setting.no_references_setting.status == "designated_answer":
        data["nodes"][6]["properties"]["node_data"]["content"] = application.knowledge_setting.value

    return data
