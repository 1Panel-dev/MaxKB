import { baseNodes } from '@/workflow/common/data'
export const applicationTemplate: any = {
  blank: {
    edges: [],
    nodes: baseNodes,
  },
  assistant: {
    nodes: [
      {
        id: 'base-node',
        type: 'base-node',
        x: 120,
        y: 260.30849999999987,
        properties: {
          config: {},
          height: 734.766,
          showNode: true,
          stepName: '基本信息',
          node_data: {
            desc: '模板',
            name: '知识库问答助手',
            prologue:
              '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务',
            tts_type: 'BROWSER',
          },
          input_field_list: [],
          user_input_config: {
            title: '用户输入',
          },
          api_input_field_list: [],
          user_input_field_list: [],
        },
      },
      {
        id: 'start-node',
        type: 'start-node',
        x: 120,
        y: 929.6914999999999,
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
            ],
          },
          fields: [
            {
              label: '用户问题',
              value: 'question',
            },
          ],
          height: 364,
          showNode: true,
          stepName: '开始',
          globalFields: [
            {
              label: '当前时间',
              value: 'time',
            },
          ],
        },
      },
      {
        id: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605',
        type: 'search-knowledge-node',
        x: 710,
        y: 929.6914999999999,
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
          height: 794,
          showNode: true,
          stepName: '知识库检索',
          condition: 'AND',
          node_data: {
            knowledge_id_list: [],
            knowledge_setting: {
              top_n: 3,
              similarity: 0.6,
              search_mode: 'embedding',
              max_paragraph_char_number: 5000,
            },
            question_reference_address: ['start-node', 'question'],
            all_knowledge_id_list: [],
            knowledge_list: [],
          },
        },
      },
      {
        id: '420a6e4f-44ff-4847-bb81-0923630846b5',
        type: 'condition-node',
        x: 1300,
        y: 929.6914999999999,
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
          height: 544.148,
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
        id: '36a440a9-5b00-4d82-b13a-8e7819112918',
        type: 'reply-node',
        x: 1890,
        y: 120,
        properties: {
          config: {
            fields: [
              {
                label: '内容',
                value: 'answer',
              },
            ],
          },
          height: 386,
          showNode: true,
          stepName: '指定回复',
          condition: 'AND',
          node_data: {
            fields: ['fd0324fc-f5e4-4fa6-a2d9-cb251b467605', 'directly_return'],
            content: '',
            is_result: true,
            reply_type: 'referencing',
          },
        },
      },
      {
        id: 'f7c3b4a2-cb80-4e47-b050-7fef0315daaf',
        type: 'ai-chat-node',
        x: 1890,
        y: 929.6914999999999,
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
            ],
          },
          height: 993.383,
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
            model_setting: {
              reasoning_content_end: '</think>',
              reasoning_content_start: '<think>',
              reasoning_content_enable: false,
            },
            dialogue_number: 1,
          },
        },
      },
      {
        id: '04dd6c1e-95f9-4757-bb3e-134d503fce54',
        type: 'reply-node',
        x: 1890,
        y: 1798.383,
        properties: {
          config: {
            fields: [
              {
                label: '内容',
                value: 'answer',
              },
            ],
          },
          height: 504,
          showNode: true,
          stepName: '指定回复1',
          condition: 'AND',
          node_data: {
            fields: [],
            content: '抱歉，没有在知识库查询到相关内容，请提供更详细的信息。',
            is_result: true,
            reply_type: 'content',
          },
        },
      },
    ],
    edges: [
      {
        id: '73f8992c-65ef-409a-a151-378d0927f2aa',
        type: 'app-edge',
        sourceNodeId: 'start-node',
        targetNodeId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605',
        startPoint: {
          x: 280,
          y: 929.6914999999999,
        },
        endPoint: {
          x: 550,
          y: 929.6914999999999,
        },
        properties: {},
        pointsList: [
          {
            x: 280,
            y: 929.6914999999999,
          },
          {
            x: 390,
            y: 929.6914999999999,
          },
          {
            x: 440,
            y: 929.6914999999999,
          },
          {
            x: 550,
            y: 929.6914999999999,
          },
        ],
        sourceAnchorId: 'start-node_right',
        targetAnchorId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605_left',
      },
      {
        id: '6a8d23d9-5179-424e-80c2-f08d37cdb8d4',
        type: 'app-edge',
        sourceNodeId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605',
        targetNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        startPoint: {
          x: 870,
          y: 929.6914999999999,
        },
        endPoint: {
          x: 1010,
          y: 929.6914999999999,
        },
        properties: {},
        pointsList: [
          {
            x: 870,
            y: 929.6914999999999,
          },
          {
            x: 980,
            y: 929.6914999999999,
          },
          {
            x: 900,
            y: 929.6914999999999,
          },
          {
            x: 1010,
            y: 929.6914999999999,
          },
        ],
        sourceAnchorId: 'fd0324fc-f5e4-4fa6-a2d9-cb251b467605_right',
        targetAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_left',
      },
      {
        id: '56006748-d9fe-491b-a14b-04fd568cac08',
        type: 'app-edge',
        sourceNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        targetNodeId: '36a440a9-5b00-4d82-b13a-8e7819112918',
        startPoint: {
          x: 1590,
          y: 793.3089999999999,
        },
        endPoint: {
          x: 1730,
          y: 120,
        },
        properties: {},
        pointsList: [
          {
            x: 1590,
            y: 793.3089999999999,
          },
          {
            x: 1700,
            y: 793.3089999999999,
          },
          {
            x: 1620,
            y: 120,
          },
          {
            x: 1730,
            y: 120,
          },
        ],
        sourceAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_7887_right',
        targetAnchorId: '36a440a9-5b00-4d82-b13a-8e7819112918_left',
      },
      {
        id: '9bc8721b-07aa-4730-9347-910ed64e26b9',
        type: 'app-edge',
        sourceNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        targetNodeId: 'f7c3b4a2-cb80-4e47-b050-7fef0315daaf',
        startPoint: {
          x: 1590,
          y: 922.6919999999999,
        },
        endPoint: {
          x: 1730,
          y: 929.6914999999999,
        },
        properties: {},
        pointsList: [
          {
            x: 1590,
            y: 922.6919999999999,
          },
          {
            x: 1700,
            y: 922.6919999999999,
          },
          {
            x: 1620,
            y: 929.6914999999999,
          },
          {
            x: 1730,
            y: 929.6914999999999,
          },
        ],
        sourceAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_6847_right',
        targetAnchorId: 'f7c3b4a2-cb80-4e47-b050-7fef0315daaf_left',
      },
      {
        id: 'c276a5b6-ec29-4ab9-b911-a0a929ff193f',
        type: 'app-edge',
        sourceNodeId: '420a6e4f-44ff-4847-bb81-0923630846b5',
        targetNodeId: '04dd6c1e-95f9-4757-bb3e-134d503fce54',
        startPoint: {
          x: 1590,
          y: 1013.3834999999998,
        },
        endPoint: {
          x: 1730,
          y: 1798.383,
        },
        properties: {},
        pointsList: [
          {
            x: 1590,
            y: 1013.3834999999998,
          },
          {
            x: 1700,
            y: 1013.3834999999998,
          },
          {
            x: 1620,
            y: 1798.383,
          },
          {
            x: 1730,
            y: 1798.383,
          },
        ],
        sourceAnchorId: '420a6e4f-44ff-4847-bb81-0923630846b5_2794_right',
        targetAnchorId: '04dd6c1e-95f9-4757-bb3e-134d503fce54_left',
      },
    ],
  },
}

export const knowledgeTemplate: any = {
  default: {
    edges: [
      {
        id: '846dd161-450e-4d2f-8119-78557d88421c',
        type: 'app-edge',
        endPoint: {
          x: 550,
          y: 720,
        },
        pointsList: [
          {
            x: 280,
            y: 720,
          },
          {
            x: 390,
            y: 720,
          },
          {
            x: 440,
            y: 720,
          },
          {
            x: 550,
            y: 720,
          },
        ],
        properties: {},
        startPoint: {
          x: 280,
          y: 720,
        },
        sourceNodeId: '768aed24-8139-4689-870f-2065ef05473c',
        targetNodeId: '1bed736e-711f-4afd-8454-2c8502444af7',
        sourceAnchorId: '768aed24-8139-4689-870f-2065ef05473c_right',
        targetAnchorId: '1bed736e-711f-4afd-8454-2c8502444af7_left',
      },
      {
        id: '79cf563e-0b4d-4d41-ad6f-4ee0c6042af6',
        type: 'app-edge',
        endPoint: {
          x: 1010,
          y: 720,
        },
        pointsList: [
          {
            x: 870,
            y: 720,
          },
          {
            x: 980,
            y: 720,
          },
          {
            x: 900,
            y: 720,
          },
          {
            x: 1010,
            y: 720,
          },
        ],
        properties: {},
        startPoint: {
          x: 870,
          y: 720,
        },
        sourceNodeId: '1bed736e-711f-4afd-8454-2c8502444af7',
        targetNodeId: '9018d6b6-be6e-420b-9a0d-7226fd789398',
        sourceAnchorId: '1bed736e-711f-4afd-8454-2c8502444af7_right',
        targetAnchorId: '9018d6b6-be6e-420b-9a0d-7226fd789398_left',
      },
      {
        id: '38111bbe-f2ff-428e-acf8-c2f49e45fb08',
        type: 'app-edge',
        endPoint: {
          x: 550,
          y: 1460,
        },
        pointsList: [
          {
            x: 280,
            y: 1460,
          },
          {
            x: 390,
            y: 1460,
          },
          {
            x: 440,
            y: 1460,
          },
          {
            x: 550,
            y: 1460,
          },
        ],
        properties: {},
        startPoint: {
          x: 280,
          y: 1460,
        },
        sourceNodeId: 'affa7bad-1898-4bdb-967b-9e12a72492c6',
        targetNodeId: 'd81adcf1-bfd4-4a1c-b62c-e9ae0eb9488d',
        sourceAnchorId: 'affa7bad-1898-4bdb-967b-9e12a72492c6_right',
        targetAnchorId: 'd81adcf1-bfd4-4a1c-b62c-e9ae0eb9488d_left',
      },
      {
        id: '632ed493-fd99-461b-9510-f4e3d02120d0',
        type: 'app-edge',
        endPoint: {
          x: 1010,
          y: 1460,
        },
        pointsList: [
          {
            x: 870,
            y: 1460,
          },
          {
            x: 980,
            y: 1460,
          },
          {
            x: 900,
            y: 1460,
          },
          {
            x: 1010,
            y: 1460,
          },
        ],
        properties: {},
        startPoint: {
          x: 870,
          y: 1460,
        },
        sourceNodeId: 'd81adcf1-bfd4-4a1c-b62c-e9ae0eb9488d',
        targetNodeId: 'a1d0fa5d-4779-4364-8b54-7eff69bd1ec4',
        sourceAnchorId: 'd81adcf1-bfd4-4a1c-b62c-e9ae0eb9488d_right',
        targetAnchorId: 'a1d0fa5d-4779-4364-8b54-7eff69bd1ec4_left',
      },
      {
        id: '5888e8cc-75fc-4df7-a627-1dc6feedea17',
        type: 'app-edge',
        endPoint: {
          x: 1790,
          y: 1440,
        },
        pointsList: [
          {
            x: 1490,
            y: 720,
          },
          {
            x: 1600,
            y: 720,
          },
          {
            x: 1680,
            y: 1440,
          },
          {
            x: 1790,
            y: 1440,
          },
        ],
        properties: {},
        startPoint: {
          x: 1490,
          y: 720,
        },
        sourceNodeId: '9018d6b6-be6e-420b-9a0d-7226fd789398',
        targetNodeId: 'ade860cd-db62-4538-9943-c8f42c1b927e',
        sourceAnchorId: '9018d6b6-be6e-420b-9a0d-7226fd789398_right',
        targetAnchorId: 'ade860cd-db62-4538-9943-c8f42c1b927e_left',
      },
      {
        id: '3f294d6b-6f4f-4a5c-9d49-f118033eec70',
        type: 'app-edge',
        endPoint: {
          x: 1790,
          y: 1440,
        },
        pointsList: [
          {
            x: 1490,
            y: 1460,
          },
          {
            x: 1600,
            y: 1460,
          },
          {
            x: 1680,
            y: 1440,
          },
          {
            x: 1790,
            y: 1440,
          },
        ],
        properties: {},
        startPoint: {
          x: 1490,
          y: 1460,
        },
        sourceNodeId: 'a1d0fa5d-4779-4364-8b54-7eff69bd1ec4',
        targetNodeId: 'ade860cd-db62-4538-9943-c8f42c1b927e',
        sourceAnchorId: 'a1d0fa5d-4779-4364-8b54-7eff69bd1ec4_right',
        targetAnchorId: 'ade860cd-db62-4538-9943-c8f42c1b927e_left',
      },
      {
        id: 'd04c1570-6572-4505-bf84-f29d81c30e57',
        type: 'app-edge',
        endPoint: {
          x: 1790,
          y: 1440,
        },
        pointsList: [
          {
            x: 1490,
            y: 2190,
          },
          {
            x: 1600,
            y: 2190,
          },
          {
            x: 1680,
            y: 1440,
          },
          {
            x: 1790,
            y: 1440,
          },
        ],
        properties: {},
        startPoint: {
          x: 1490,
          y: 2190,
        },
        sourceNodeId: 'dddebd93-ea1a-4880-8a52-ea8112f7e769',
        targetNodeId: 'ade860cd-db62-4538-9943-c8f42c1b927e',
        sourceAnchorId: 'dddebd93-ea1a-4880-8a52-ea8112f7e769_right',
        targetAnchorId: 'ade860cd-db62-4538-9943-c8f42c1b927e_left',
      },
      {
        id: '536d7d47-9ad8-4144-a6df-35e3e2398327',
        type: 'app-edge',
        endPoint: {
          x: 2430,
          y: 1430,
        },
        pointsList: [
          {
            x: 2110,
            y: 1440,
          },
          {
            x: 2220,
            y: 1440,
          },
          {
            x: 2320,
            y: 1430,
          },
          {
            x: 2430,
            y: 1430,
          },
        ],
        properties: {},
        startPoint: {
          x: 2110,
          y: 1440,
        },
        sourceNodeId: 'ade860cd-db62-4538-9943-c8f42c1b927e',
        targetNodeId: '1c5abed5-e181-41f7-96f5-b5175cc37f3c',
        sourceAnchorId: 'ade860cd-db62-4538-9943-c8f42c1b927e_right',
        targetAnchorId: '1c5abed5-e181-41f7-96f5-b5175cc37f3c_left',
      },
      {
        id: '8b5bb2b5-5baa-4e54-b848-fa87231d9585',
        type: 'app-edge',
        endPoint: {
          x: 1010,
          y: 2190,
        },
        pointsList: [
          {
            x: 870,
            y: 2190,
          },
          {
            x: 980,
            y: 2190,
          },
          {
            x: 900,
            y: 2190,
          },
          {
            x: 1010,
            y: 2190,
          },
        ],
        properties: {},
        startPoint: {
          x: 870,
          y: 2190,
        },
        sourceNodeId: '08503db8-f2e3-4eb3-96f7-957f30a6da6e',
        targetNodeId: 'dddebd93-ea1a-4880-8a52-ea8112f7e769',
        sourceAnchorId: '08503db8-f2e3-4eb3-96f7-957f30a6da6e_right',
        targetAnchorId: 'dddebd93-ea1a-4880-8a52-ea8112f7e769_left',
      },
    ],
    nodes: [
      {
        x: 120,
        y: 115.05849999999998,
        id: 'knowledge-base-node',
        type: 'knowledge-base-node',
        properties: {
          config: {
            fields: [],
            globalFields: [],
          },
          height: 394.383,
          showNode: true,
          stepName: '\u57fa\u672c\u4fe1\u606f',
          node_data: {
            desc: '',
            name: '',
            prologue:
              '\u60a8\u597d\uff0c\u6211\u662f XXX \u5c0f\u52a9\u624b\uff0c\u60a8\u53ef\u4ee5\u5411\u6211\u63d0\u51fa XXX \u4f7f\u7528\u95ee\u9898\u3002\n- XXX \u4e3b\u8981\u529f\u80fd\u6709\u4ec0\u4e48\uff1f\n- XXX \u5982\u4f55\u6536\u8d39\uff1f\n- \u9700\u8981\u8f6c\u4eba\u5de5\u670d\u52a1',
            tts_type: 'BROWSER',
          },
          input_field_list: [],
          user_input_config: {
            title: '\u6587\u6863\u5904\u7406\u8bbe\u7f6e',
          },
          user_input_field_list: [],
        },
      },
      {
        x: 120,
        y: 720,
        id: '768aed24-8139-4689-870f-2065ef05473c',
        type: 'data-source-local-node',
        properties: {
          kind: 'data-source',
          config: {
            fields: [
              {
                label: '\u6587\u4ef6\u5217\u8868',
                value: 'file_list',
              },
            ],
          },
          height: 566,
          showNode: true,
          stepName: '\u6587\u672c\u6587\u4ef6',
          node_data: {
            file_type_list: ['TXT', 'DOCX', 'PDF', 'HTML', 'XLS', 'XLSX', 'CSV'],
            file_size_limit: 100,
            file_count_limit: 50,
          },
          input_field_list: [],
          user_input_config: {},
          user_input_field_list: [],
        },
      },
      {
        x: 710,
        y: 720,
        id: '1bed736e-711f-4afd-8454-2c8502444af7',
        type: 'document-extract-node',
        properties: {
          config: {
            fields: [
              {
                label: '\u6587\u6863\u5185\u5bb9',
                value: 'content',
              },
              {
                label: '\u6587\u6863\u5217\u8868',
                value: 'document_list',
              },
            ],
          },
          height: 394,
          showNode: true,
          stepName: '\u6587\u6863\u5185\u5bb9\u63d0\u53d6',
          condition: 'OR',
          node_data: {
            document_list: ['768aed24-8139-4689-870f-2065ef05473c', 'file_list'],
          },
        },
      },
      {
        x: 1250,
        y: 2190,
        id: 'dddebd93-ea1a-4880-8a52-ea8112f7e769',
        type: 'document-split-node',
        properties: {
          width: 500,
          config: {
            fields: [
              {
                label: '\u5206\u6bb5\u5217\u8868',
                value: 'paragraph_list',
              },
            ],
          },
          height: 652,
          showNode: true,
          stepName: 'Web\u667a\u80fd\u5206\u6bb5',
          condition: 'AND',
          node_data: {
            limit: 4096,
            patterns: [],
            chunk_size: 256,
            limit_type: 'custom',
            with_filter: false,
            document_list: ['08503db8-f2e3-4eb3-96f7-957f30a6da6e', 'document_list'],
            patterns_type: 'custom',
            split_strategy: 'auto',
            chunk_size_type: 'custom',
            limit_reference: [],
            with_filter_type: 'custom',
            patterns_reference: [],
            chunk_size_reference: [],
            with_filter_reference: [],
            document_name_relate_problem: false,
            paragraph_title_relate_problem: true,
            document_name_relate_problem_type: 'custom',
            paragraph_title_relate_problem_type: 'custom',
            document_name_relate_problem_reference: [],
            paragraph_title_relate_problem_reference: [],
          },
        },
      },
      {
        x: 2590,
        y: 1430,
        id: '1c5abed5-e181-41f7-96f5-b5175cc37f3c',
        type: 'knowledge-write-node',
        properties: {
          config: {
            fields: [],
          },
          height: 278,
          showNode: true,
          stepName: '\u77e5\u8bc6\u5e93\u5199\u5165',
          condition: 'AND',
          node_data: {
            document_list: ['ade860cd-db62-4538-9943-c8f42c1b927e', 'Segmented_List'],
          },
        },
      },
      {
        x: 1250,
        y: 720,
        id: '9018d6b6-be6e-420b-9a0d-7226fd789398',
        type: 'document-split-node',
        properties: {
          width: 500,
          config: {
            fields: [
              {
                label: '\u5206\u6bb5\u5217\u8868',
                value: 'paragraph_list',
              },
            ],
          },
          height: 652,
          showNode: true,
          stepName: '\u667a\u80fd\u5206\u6bb5',
          condition: 'AND',
          node_data: {
            limit: 4096,
            patterns: [],
            chunk_size: 256,
            limit_type: 'custom',
            with_filter: false,
            document_list: ['1bed736e-711f-4afd-8454-2c8502444af7', 'document_list'],
            patterns_type: 'custom',
            split_strategy: 'auto',
            chunk_size_type: 'custom',
            limit_reference: [],
            with_filter_type: 'custom',
            patterns_reference: [],
            chunk_size_reference: [],
            with_filter_reference: [],
            document_name_relate_problem: true,
            paragraph_title_relate_problem: true,
            document_name_relate_problem_type: 'custom',
            paragraph_title_relate_problem_type: 'custom',
            document_name_relate_problem_reference: [],
            paragraph_title_relate_problem_reference: [],
          },
        },
      },
      {
        x: 120,
        y: 1460,
        id: 'affa7bad-1898-4bdb-967b-9e12a72492c6',
        type: 'data-source-local-node',
        properties: {
          kind: 'data-source',
          config: {
            fields: [
              {
                label: '\u6587\u4ef6\u5217\u8868',
                value: 'file_list',
              },
            ],
          },
          height: 536,
          showNode: true,
          stepName: 'QA\u95ee\u7b54\u5bf9',
          node_data: {
            file_type_list: ['XLS', 'XLSX', 'CSV', 'ZIP'],
            file_size_limit: 100,
            file_count_limit: 50,
          },
          input_field_list: [],
          user_input_config: {},
          user_input_field_list: [],
        },
      },
      {
        x: 710,
        y: 1460,
        id: 'd81adcf1-bfd4-4a1c-b62c-e9ae0eb9488d',
        type: 'document-extract-node',
        properties: {
          config: {
            fields: [
              {
                label: '\u6587\u6863\u5185\u5bb9',
                value: 'content',
              },
              {
                label: '\u6587\u6863\u5217\u8868',
                value: 'document_list',
              },
            ],
          },
          height: 394,
          showNode: true,
          stepName: '\u6587\u6863\u5185\u5bb9\u63d0\u53d61',
          condition: 'AND',
          node_data: {
            document_list: ['affa7bad-1898-4bdb-967b-9e12a72492c6', 'file_list'],
          },
        },
      },
      {
        x: 1250,
        y: 1460,
        id: 'a1d0fa5d-4779-4364-8b54-7eff69bd1ec4',
        type: 'document-split-node',
        properties: {
          width: 500,
          config: {
            fields: [
              {
                label: '\u5206\u6bb5\u5217\u8868',
                value: 'paragraph_list',
              },
            ],
          },
          height: 580,
          showNode: true,
          stepName: 'QA\u95ee\u7b54\u5bf9\u5206\u6bb5',
          condition: 'AND',
          node_data: {
            limit: 4096,
            patterns: [],
            chunk_size: 256,
            limit_type: 'custom',
            with_filter: false,
            document_list: ['d81adcf1-bfd4-4a1c-b62c-e9ae0eb9488d', 'document_list'],
            patterns_type: 'custom',
            split_strategy: 'qa',
            chunk_size_type: 'custom',
            limit_reference: [],
            with_filter_type: 'custom',
            patterns_reference: [],
            chunk_size_reference: [],
            with_filter_reference: [],
            document_name_relate_problem: true,
            paragraph_title_relate_problem: false,
            document_name_relate_problem_type: 'custom',
            paragraph_title_relate_problem_type: 'custom',
            document_name_relate_problem_reference: [],
            paragraph_title_relate_problem_reference: [],
          },
        },
      },
      {
        x: 1950,
        y: 1440,
        id: 'ade860cd-db62-4538-9943-c8f42c1b927e',
        type: 'variable-aggregation-node',
        properties: {
          config: {
            fields: [
              {
                label: '\u6587\u6863\u5206\u6bb5\u5217\u8868',
                value: 'Segmented_List',
              },
            ],
          },
          height: 570.7660000000001,
          showNode: true,
          stepName: '\u805a\u5408\u6587\u6863\u5206\u6bb5\u5217\u8868',
          condition: 'OR',
          node_data: {
            strategy: 'first_non_null',
            is_result: true,
            group_list: [
              {
                id: 'kU2zR8yRzNIt3RXKHmJtL',
                field: 'Segmented_List',
                label: '\u6587\u6863\u5206\u6bb5\u5217\u8868',
                variable_list: [
                  {
                    v_id: 'N59Lo_VyRKuYASHaKN6g0',
                    variable: ['9018d6b6-be6e-420b-9a0d-7226fd789398', 'paragraph_list'],
                  },
                  {
                    v_id: 'IRQkWPB7THGXlkSBCWmkY',
                    variable: ['a1d0fa5d-4779-4364-8b54-7eff69bd1ec4', 'paragraph_list'],
                  },
                  {
                    v_id: 'jGrIINd-6O6UEzNmZvFap',
                    variable: ['dddebd93-ea1a-4880-8a52-ea8112f7e769', 'paragraph_list'],
                  },
                ],
              },
            ],
          },
        },
      },
      {
        x: 710,
        y: 2190,
        id: '08503db8-f2e3-4eb3-96f7-957f30a6da6e',
        type: 'data-source-web-node',
        properties: {
          kind: 'data-source',
          config: {
            fields: [
              {
                label: '\u6587\u6863\u5217\u8868',
                value: 'document_list',
              },
            ],
          },
          height: 292,
          showNode: true,
          stepName: 'Web\u7ad9\u70b9',
        },
      },
    ],
  },
}
