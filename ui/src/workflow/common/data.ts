import { WorkflowType } from '@/enums/workflow'

export const startNode = {
  id: WorkflowType.Start,
  type: WorkflowType.Start,
  x: 180,
  y: 720,
  properties: {
    height: 200,
    stepName: '开始',
    config: {
      fields: [
        {
          label: '用户问题',
          value: 'question'
        }
      ],
      globalFields: [
        {
          value: 'time',
          label: '当前时间'
        }
      ]
    }
  }
}
export const baseNode = {
  id: WorkflowType.Base,
  type: WorkflowType.Base,
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
    },
    config: {}
  }
}
/**
 * 说明
 * type 与 nodes 文件对应
 */
export const baseNodes = [baseNode, startNode]
/**
 * ai对话节点配置数据
 */
export const aiChatNode = {
  type: WorkflowType.AiChat,
  text: '与 AI 大模型进行对话',
  label: 'AI 对话',
  properties: {
    stepName: 'AI 对话',
    config: {
      fields: [
        {
          label: 'AI 回答内容',
          value: 'answer'
        }
      ]
    }
  }
}
/**
 * 知识库检索配置数据
 */
export const searchDatasetNode = {
  type: WorkflowType.SearchDataset,
  text: '关联知识库，查找与问题相关的分段',
  label: '知识库检索',
  properties: {
    stepName: '知识库检索',
    config: {
      fields: [
        { label: '检索结果的分段列表', value: 'paragraph_list' },
        { label: '满足直接回答的分段列表', value: 'is_hit_handling_method_list' },
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
  }
}
export const questionNode = {
  type: WorkflowType.Question,
  text: '根据历史聊天记录优化完善当前问题，更利于匹配知识库分段',
  label: '问题优化',
  properties: {
    stepName: '问题优化',
    config: {
      fields: [
        {
          label: '问题优化结果',
          value: 'answer'
        }
      ]
    }
  }
}
export const conditionNode = {
  type: WorkflowType.Condition,
  text: '根据不同条件执行不同的节点',
  label: '判断器',
  properties: {
    width: 600,
    stepName: '判断器',
    config: {
      fields: [
        {
          label: '分支名称',
          value: 'branch_name'
        }
      ]
    }
  }
}
export const replyNode = {
  type: WorkflowType.Reply,
  text: '指定回复内容，引用变量会转换为字符串进行输出',
  label: '指定回复',
  properties: {
    stepName: '指定回复',
    config: {
      fields: [
        {
          label: '内容',
          value: 'answer'
        }
      ]
    }
  }
}
export const menuNodes = [aiChatNode, searchDatasetNode, questionNode, conditionNode, replyNode]

export const compareList = [
  { value: 'is_null', label: '为空' },
  { value: 'is_not_null', label: '不为空' },
  { value: 'contain', label: '包含' },
  { value: 'not_contain', label: '不包含' },
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

export const nodeDict: any = {
  [WorkflowType.AiChat]: aiChatNode,
  [WorkflowType.SearchDataset]: searchDatasetNode,
  [WorkflowType.Question]: questionNode,
  [WorkflowType.Condition]: conditionNode,
  [WorkflowType.Base]: baseNode,
  [WorkflowType.Start]: startNode,
  [WorkflowType.Reply]: replyNode
}
export function isWorkFlow(type: string | undefined) {
  return type === 'WORK_FLOW'
}
