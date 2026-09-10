import type LogicFlow from '@logicflow/core'
import { defaultApplicationNodes } from '@/workflow-canvas/config/node-mapping'

export const applicationTemplate = {
  blank: { edges: [], nodes: defaultApplicationNodes },
  assistant: {
    nodes: [
      {
        x: 131.39509127035535,
        y: 455.9261768016129,
        id: 'base-node',
        type: 'base-node',
        properties: {
          width: 600,
          config: {},
          height: 725,
          showNode: true,
          stepName: '基本信息',
          node_data: {
            desc: '基于用户问题，检索知识库相关内容作为AI模型的参考内容',
            name: '知识库问答助手',
            prologue: '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务',
            tts_type: 'BROWSER',
            stt_model_id_type: 'default',
            long_term_model_id_type: 'default',
          },
          enableException: false,
          input_field_list: [],
          user_input_config: {
            title: '用户输入',
          },
          api_input_field_list: [],
          chat_input_field_list: [],
          user_input_field_list: [],
        },
      },
      {
        x: 715.0184297448741,
        y: 320.4313532704871,
        id: 'start-node',
        type: 'start-node',
        properties: {
          config: {
            fields: [
              {
                label: '用户问题',
                value: 'question',
              },
            ],
            globalFields: [
              {
                label: '当前时间',
                value: 'time',
              },
              {
                label: '历史聊天记录',
                value: 'history_context',
              },
              {
                label: '对话 ID',
                value: 'chat_id',
              },
              {
                label: '对话用户 ID',
                value: 'chat_user_id',
              },
              {
                label: '对话用户类型',
                value: 'chat_user_type',
              },
              {
                label: '对话用户组',
                value: 'chat_user_group',
              },
              {
                label: '对话用户',
                value: 'chat_user',
              },
            ],
            chatFields: [],
          },
          fields: [
            {
              label: '用户问题',
              value: 'question',
            },
          ],
          height: 556,
          showNode: true,
          stepName: '开始',
          globalFields: [
            {
              label: '当前时间',
              value: 'time',
            },
          ],
          enableException: false,
        },
      },
      {
        x: 1211.870063753232,
        y: 443.29042897959704,
        id: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605',
        type: 'search-knowledge-node',
        properties: {
          config: {
            fields: [
              {
                label: '检索结果的分段列表',
                value: 'paragraph_list',
              },
              {
                label: '满足直接回答的分段列表',
                value: 'is_hit_handling_method_list',
              },
              {
                label: '检索结果',
                value: 'data',
              },
              {
                label: '满足直接回答的分段内容',
                value: 'directly_return',
              },
            ],
          },
          height: 806.383,
          showNode: true,
          stepName: '知识库检索',
          condition: 'AND',
          node_data: {
            knowledge_list: [],
            show_knowledge: false,
            knowledge_id_list: [],
            knowledge_setting: {
              top_n: 3,
              similarity: 0.6,
              search_mode: 'embedding',
              max_paragraph_char_number: 5000,
            },
            search_scope_type: 'custom',
            search_scope_source: 'knowledge',
            all_knowledge_id_list: [],
            question_reference_address: ['start-node', 'question'],
            no_permission_knowledge_id_list: [],
          },
          enableException: false,
        },
      },
      {
        x: 1822.6628761517477,
        y: 376.8206988860253,
        id: '420a6e4f-44ff-4847-bb81-0923630846b5',
        type: 'condition-node',
        properties: {
          width: 600,
          config: {
            fields: [
              {
                label: '分支名称',
                value: 'branch_name',
              },
            ],
          },
          height: 552.148,
          showNode: true,
          stepName: '判断器',
          condition: 'AND',
          node_data: {
            branch: [
              {
                id: '7887',
                type: 'IF',
                condition: 'and',
                conditions: [
                  {
                    field: ['fd0324fc-f5e4-4fa6-a2d9-cb251b467605', 'is_hit_handling_method_list'],
                    value: 1,
                    compare: 'is_not_null',
                  },
                ],
              },
              {
                id: '6847',
                type: 'ELSE IF 1',
                condition: 'and',
                conditions: [
                  {
                    field: ['fd0324fc-f5e4-4fa6-a2d9-cb251b467605', 'paragraph_list'],
                    value: 1,
                    compare: 'is_not_null',
                  },
                ],
              },
              {
                id: '2794',
                type: 'ELSE',
                condition: 'and',
                conditions: [],
              },
            ],
          },
          enableException: false,
          branch_condition_list: [
            {
              index: 0,
              height: 121.383,
              id: '7887',
            },
            {
              index: 1,
              height: 121.383,
              id: '6847',
            },
            {
              index: 2,
              height: 44,
              id: '2794',
            },
          ],
        },
      },
      {
        x: 2487.238292469783,
        y: -96.76253793813842,
        id: '36a440a9-5b00-4d82-b13a-8e7819112918',
        type: 'reply-node',
        properties: {
          config: {
            fields: [
              {
                label: '内容',
                value: 'answer',
              },
            ],
          },
          height: 394,
          showNode: true,
          stepName: '指定回复',
          condition: 'AND',
          node_data: {
            fields: ['fd0324fc-f5e4-4fa6-a2d9-cb251b467605', 'directly_return'],
            content: '',
            is_result: true,
            reply_type: 'referencing',
          },
          enableException: false,
        },
      },
      {
        x: 2488.3008451532673,
        y: 660.574819248909,
        id: 'f7c3b4a2-cb80-4e47-b050-7fef0315daaf',
        type: 'ai-chat-node',
        properties: {
          config: {
            fields: [
              {
                label: 'AI 回答内容',
                value: 'answer',
              },
              {
                label: '思考过程',
                value: 'reasoning_content',
              },
              {
                label: '历史聊天记录',
                value: 'history_message',
              },
            ],
          },
          height: 1174.38,
          showNode: true,
          stepName: 'AI 对话',
          condition: 'AND',
          node_data: {
            prompt: '已知信息：\n{{知识库检索.data}}\n问题：\n{{开始.question}}',
            system: '',
            model_id: '',
            is_result: true,
            max_tokens: null,
            temperature: null,
            dialogue_type: 'WORKFLOW',
            model_id_type: 'default',
            model_setting: {
              reasoning_content_end: '</think>',
              reasoning_content_start: '<think>',
              reasoning_content_enable: false,
            },
            dialogue_number: 1,
            mcp_output_enable: true,
            model_id_reference: [],
          },
          enableException: false,
        },
      },
      {
        x: 2489.758837821939,
        y: 1491.5462871796265,
        id: '04dd6c1e-95f9-4757-bb3e-134d503fce54',
        type: 'reply-node',
        properties: {
          config: {
            fields: [
              {
                label: '内容',
                value: 'answer',
              },
            ],
          },
          height: 512,
          showNode: true,
          stepName: '指定回复1',
          condition: 'AND',
          node_data: {
            fields: [],
            content: '抱歉，没有在知识库查询到相关内容，请提供更详细的信息。',
            is_result: true,
            reply_type: 'content',
          },
          enableException: false,
        },
      },
    ],
    edges: [
      {
        id: '73f8992c-65ef-409a-a151-378d0927f2aa',
        type: 'app-edge',
        endPoint: {
          x: 1051.870063753232,
          y: 443.29042897959704,
        },
        pointsList: [
          {
            x: 875.0184297448741,
            y: 320.4313532704871,
          },
          {
            x: 975.0184297448741,
            y: 320.4313532704871,
          },
          {
            x: 951.870063753232,
            y: 443.29042897959704,
          },
          {
            x: 1051.870063753232,
            y: 443.29042897959704,
          },
        ],
        properties: {},
        startPoint: {
          x: 875.0184297448741,
          y: 320.4313532704871,
        },
        sourceNodeId: 'start-node',
        targetNodeId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605',
        sourceAnchorId: 'start-node_right',
        targetAnchorId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605_left',
      },
      {
        id: '6a8d23d9-5179-424e-80c2-f08d37cdb8d4',
        type: 'app-edge',
        endPoint: {
          x: 1522.6628761517477,
          y: 376.8206988860253,
        },
        pointsList: [
          {
            x: 1371.870063753232,
            y: 443.29042897959704,
          },
          {
            x: 1471.870063753232,
            y: 443.29042897959704,
          },
          {
            x: 1422.6628761517477,
            y: 376.8206988860253,
          },
          {
            x: 1522.6628761517477,
            y: 376.8206988860253,
          },
        ],
        properties: {},
        startPoint: {
          x: 1371.870063753232,
          y: 443.29042897959704,
        },
        sourceNodeId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605',
        targetNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        sourceAnchorId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605_right',
        targetAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_left',
      },
      {
        id: '56006748-d9fe-491b-a14b-04fd568cac08',
        type: 'app-edge',
        endPoint: {
          x: 2327.238292469783,
          y: -96.76253793813842,
        },
        pointsList: [
          {
            x: 2122.662876151749,
            y: 236.8206988860253,
          },
          {
            x: 2222.662876151749,
            y: 236.8206988860253,
          },
          {
            x: 2227.238292469783,
            y: -96.76253793813842,
          },
          {
            x: 2327.238292469783,
            y: -96.76253793813842,
          },
        ],
        properties: {},
        startPoint: {
          x: 2122.662876151749,
          y: 236.8206988860253,
        },
        sourceNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        targetNodeId: '36a440a9-5b00-4d82-b13a-8e7819112918',
        sourceAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_7887_right',
        targetAnchorId: '36a440a9-5b00-4d82-b13a-8e7819112918_left',
      },
      {
        id: '9bc8721b-07aa-4730-9347-910ed64e26b9',
        type: 'app-edge',
        endPoint: {
          x: 2328.3008451532673,
          y: 660.574819248909,
        },
        pointsList: [
          {
            x: 2122.662876151749,
            y: 383.8206988860253,
          },
          {
            x: 2222.662876151749,
            y: 383.8206988860253,
          },
          {
            x: 2228.3008451532673,
            y: 660.574819248909,
          },
          {
            x: 2328.3008451532673,
            y: 660.574819248909,
          },
        ],
        properties: {},
        startPoint: {
          x: 2122.662876151749,
          y: 383.8206988860253,
        },
        sourceNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        targetNodeId: 'f7c3b4a2-cb80-4e47-b050-7fef0315daaf',
        sourceAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_6847_right',
        targetAnchorId: 'f7c3b4a2-cb80-4e47-b050-7fef0315daaf_left',
      },
      {
        id: 'c276a5b6-ec29-4ab9-b911-a0a929ff193f',
        type: 'app-edge',
        endPoint: {
          x: 2329.758837821939,
          y: 1491.5462871796265,
        },
        pointsList: [
          {
            x: 2122.662876151749,
            y: 503.8206988860254,
          },
          {
            x: 2222.662876151749,
            y: 503.8206988860254,
          },
          {
            x: 2229.758837821939,
            y: 1491.5462871796265,
          },
          {
            x: 2329.758837821939,
            y: 1491.5462871796265,
          },
        ],
        properties: {},
        startPoint: {
          x: 2122.662876151749,
          y: 503.8206988860254,
        },
        sourceNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        targetNodeId: '04dd6c1e-95f9-4757-bb3e-134d503fce54',
        sourceAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_2794_right',
        targetAnchorId: '04dd6c1e-95f9-4757-bb3e-134d503fce54_left',
      },
    ],
  },
} satisfies Record<string, LogicFlow.GraphConfigData>
