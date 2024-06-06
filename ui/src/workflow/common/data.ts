/**
 * 说明
 * type 与 nodes 文件对应
 */
export const baseNodes = [
  {
    id: 'base-node',
    type: 'base-node',
    x: 200,
    y: 270,
    properties: {
      height: 200,
      stepName: '基本信息',
      node_data: {
        name: '',
        desc: '',
        prologue: ''
      }
    }
  },
  {
    id: 'start-node',
    type: 'start-node',
    x: 180,
    y: 720,
    properties: {
      height: 200,
      stepName: '开始',
      output: [{ key: '' }],
      fields: [
        {
          label: '用户问题',
          value: 'question'
        }
      ]
    }
  }
]

export const menuNodes = [
  {
    type: 'ai-chat-node',
    text: '与 AI 大模型进行对话',
    label: 'AI 对话',
    icon: 'ai-chat-node-icon',
    properties: {
      height: '',
      stepName: 'AI 对话',
      input: [
        {
          key: ''
        }
      ],
      output: [
        {
          key: ''
        }
      ],
      fields: [
        {
          label: 'AI 回答内容',
          value: 'content'
        }
      ]
    }
  },
  {
    type: 'search-dataset-node',
    text: '关联知识库，查找与问题相关的分段',
    label: '知识库检索',
    icon: 'search-dataset-node-icon',
    properties: {
      height: '',
      stepName: '知识库检索',
      input: [
        {
          key: '输入'
        }
      ],
      output: [
        {
          key: '输出'
        }
      ],
      fields: [
        {
          label: '检索结果',
          value: 'data'
        },
        {
          label: '满足直接回答的分段内容',
          value: 'paragraph'
        }
      ]
    }
  },
  {
    type: 'condition-node',
    text: '根据不同条件执行不同的节点',
    label: '判断器',
    icon: 'condition-node-icon',
    properties: {
      width: 600,
      stepName: '判断器',
      input: [
        {
          key: '输入'
        }
      ],
      output: [
        {
          key: '输出'
        }
      ]
    }
  }
]
