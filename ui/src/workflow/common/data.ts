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
        prologue:
          '您好，我是 MaxKB 小助手，您可以向我提出 MaxKB 使用问题。\n- MaxKB 主要功能有什么？\n- MaxKB 支持哪些大语言模型？\n- MaxKB 支持哪些文档类型？'
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
      fields: [
        {
          label: '用户问题',
          value: 'question',
          globeLabel: '{{开始.question}}',
          globeValue: "{{content['start-node'].question}}"
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
      fields: [
        {
          label: 'AI 回答内容',
          value: 'answer'
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
      fields: [
        { label: '段落列表', value: 'paragraph_list' },
        { label: '满足直接回答的段落列表', value: 'is_hit_handling_method_list' },
        {
          label: '检索结果',
          value: 'data'
        },
        {
          label: '满足直接回答的分段内容',
          value: 'directly_return'
        }
      ]
    }
  },
  {
    type: 'question-node',
    text: '根据历史聊天记录优化完善当前问题，更利于匹配知识库分段',
    label: '问题优化',
    icon: 'question-node-icon',
    properties: {
      height: '',
      stepName: '问题优化',
      fields: [
        {
          label: '问题优化结果',
          value: 'answer'
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
      stepName: '判断器'
    }
  },
  {
    type: 'reply-node',
    text: '指定回复内容，引用变量会转换为字符串进行输出',
    label: '指定回复',
    icon: 'reply-node-icon',
    properties: {
      height: '',
      stepName: '指定回复'
    }
  }
]

export const compareList = [
  { value: 'contain', label: '包含' },
  { value: 'eq', label: '等于' },
  { value: 'ge', label: '大于等于' },
  { value: 'gt', label: '大于' },
  { value: 'le', label: '小于等于' },
  { value: 'len_eq', label: '长度等于' },
  { value: 'len_ge', label: '长度大于等于' },
  { value: 'len_gt', label: '长度大于' },
  { value: 'len_le', label: '长度小于等于' },
  { value: 'len_lt', label: '长度小于' },
  { value: 'lt', label: '小于' }
]
