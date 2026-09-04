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
          stepName: '\u57fa\u672c\u4fe1\u606f',
          condition: 'AND',
          node_data: {
            desc: '',
            name: 'dan-template',
            prologue:
              '\u60a8\u597d\uff0c\u6211\u662f XXX \u5c0f\u52a9\u624b\uff0c\u60a8\u53ef\u4ee5\u5411\u6211\u63d0\u51fa XXX \u4f7f\u7528\u95ee\u9898\u3002\n- XXX \u4e3b\u8981\u529f\u80fd\u6709\u4ec0\u4e48\uff1f\n- XXX \u5982\u4f55\u6536\u8d39\uff1f\n- \u9700\u8981\u8f6c\u4eba\u5de5\u670d\u52a1',
            tts_type: 'BROWSER',
            stt_autosend: false,
            stt_model_id: '',
            tts_autoplay: false,
            tts_model_id: '',
            long_term_enable: false,
            stt_model_enable: false,
            tts_model_enable: false,
            stt_model_id_type: 'default',
            file_upload_enable: false,
            long_term_model_id: '',
            file_upload_setting: {
              audio: false,
              image: false,
              other: false,
              video: false,
              document: true,
              maxFiles: 3,
              fileLimit: 50,
              url_upload: false,
              local_upload: true,
              otherExtensions: ['PPT', 'DOC'],
            },
            long_term_trigger_type: 'ROUND',
            long_term_model_id_type: 'default',
            tts_model_params_setting: {},
            long_term_trigger_setting: {
              rounds: 10,
            },
            long_term_model_params_setting: {},
          },
          enableException: false,
          input_field_list: [],
          user_input_config: {
            title: '\u7528\u6237\u8f93\u5165',
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
          width: 320,
          config: {
            fields: [
              {
                label: '\u7528\u6237\u95ee\u9898',
                value: 'question',
              },
            ],
            chatFields: [],
            globalFields: [
              {
                label: '\u5f53\u524d\u65f6\u95f4',
                value: 'time',
              },
              {
                label: '\u5386\u53f2\u804a\u5929\u8bb0\u5f55',
                value: 'history_context',
              },
              {
                label: '\u5bf9\u8bdd ID',
                value: 'chat_id',
              },
              {
                label: '\u5bf9\u8bdd\u7528\u6237 ID',
                value: 'chat_user_id',
              },
              {
                label: '\u5bf9\u8bdd\u7528\u6237\u7c7b\u578b',
                value: 'chat_user_type',
              },
              {
                label: '\u5bf9\u8bdd\u7528\u6237\u7ec4',
                value: 'chat_user_group',
              },
              {
                label: '\u5bf9\u8bdd\u7528\u6237',
                value: 'chat_user',
              },
            ],
          },
          fields: [
            {
              label: '\u7528\u6237\u95ee\u9898',
              value: 'question',
            },
          ],
          height: 456,
          showNode: true,
          stepName: '\u5f00\u59cb',
          condition: 'AND',
          enableException: false,
        },
      },
      {
        x: 1211.870063753232,
        y: 443.29042897959704,
        id: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605',
        type: 'search-knowledge-node',
        properties: {
          width: 320,
          config: {
            fields: [
              {
                label: '\u68c0\u7d22\u7ed3\u679c\u7684\u5206\u6bb5\u5217\u8868',
                value: 'paragraph_list',
              },
              {
                label: '\u6ee1\u8db3\u76f4\u63a5\u56de\u7b54\u7684\u5206\u6bb5\u5217\u8868',
                value: 'is_hit_handling_method_list',
              },
              {
                label: '\u68c0\u7d22\u7ed3\u679c',
                value: 'data',
              },
              {
                label: '\u6ee1\u8db3\u76f4\u63a5\u56de\u7b54\u7684\u5206\u6bb5\u5185\u5bb9',
                value: 'directly_return',
              },
            ],
          },
          height: 698,
          showNode: true,
          stepName: '\u77e5\u8bc6\u5e93\u68c0\u7d22',
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
            search_scope_reference: [],
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
          width: 320,
          config: {
            fields: [
              {
                label: '\u5206\u652f\u540d\u79f0',
                value: 'branch_name',
              },
            ],
          },
          height: 569,
          showNode: true,
          stepName: '\u5224\u65ad\u5668',
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
              id: '7887',
              index: 0,
              height: 139,
            },
            {
              id: '6847',
              index: 1,
              height: 139,
            },
            {
              id: '2794',
              index: 2,
              height: 85,
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
          width: 320,
          config: {
            fields: [
              {
                label: '\u5185\u5bb9',
                value: 'answer',
              },
            ],
          },
          height: 279.375,
          showNode: true,
          stepName: '\u6307\u5b9a\u56de\u590d',
          condition: 'AND',
          node_data: {
            fields: ['fd0324fc-f5e4-4fa6-a2d9-cb251b467605', 'directly_return'],
            content: '12323232',
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
          width: 320,
          config: {
            fields: [
              {
                label: 'AI \u56de\u7b54\u5185\u5bb9',
                value: 'answer',
              },
              {
                label: '\u601d\u8003\u8fc7\u7a0b',
                value: 'reasoning_content',
              },
            ],
          },
          height: 1134,
          showNode: true,
          stepName: 'AI \u5bf9\u8bdd',
          condition: 'AND',
          node_data: {
            prompt: '\u5df2\u77e5\u4fe1\u606f\uff1a\n{{\u77e5\u8bc6\u5e93\u68c0\u7d22.data}}\n\u95ee\u9898\uff1a\n{{\u5f00\u59cb.question}}',
            system: '',
            vision: false,
            model_id: '',
            tool_ids: [],
            is_result: true,
            image_list: [],
            max_tokens: null,
            mcp_source: 'referencing',
            video_list: [],
            mcp_servers: '',
            temperature: null,
            mcp_tool_ids: [],
            dialogue_type: 'WORKFLOW',
            model_id_type: 'custom',
            model_setting: {
              reasoning_content_end: '</think>',
              reasoning_content_start: '<think>',
              reasoning_content_enable: false,
            },
            skill_tool_ids: [],
            application_ids: [],
            dialogue_number: 1,
            mcp_output_enable: true,
            model_id_reference: [],
            model_params_setting: {},
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
          width: 320,
          config: {
            fields: [
              {
                label: '\u5185\u5bb9',
                value: 'answer',
              },
            ],
          },
          height: 397.375,
          showNode: true,
          stepName: '\u6307\u5b9a\u56de\u590d1',
          condition: 'AND',
          node_data: {
            fields: [],
            content:
              '\u62b1\u6b49\uff0c\u6ca1\u6709\u5728\u77e5\u8bc6\u5e93\u67e5\u8be2\u5230\u76f8\u5173\u5185\u5bb9\uff0c\u8bf7\u63d0\u4f9b\u66f4\u8be6\u7ec6\u7684\u4fe1\u606f\u3002',
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
