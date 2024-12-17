import { WorkflowType } from '@/enums/workflow'
import { t } from '@/locales'

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
  text: '',
  properties: {
    width: 420,
    height: 200,
    stepName: '基本信息',
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      // @ts-ignore
      prologue: t('views.application.prompt.defaultPrologue')
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
  height: 340,
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
  height: 355,
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
  height: 345,
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
  height: 175,
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
  height: 210,
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
export const rerankerNode = {
  type: WorkflowType.RrerankerNode,
  text: '使用重排模型对多个知识库的检索结果进行二次召回',
  label: '多路召回',
  height: 252,
  properties: {
    stepName: '多路召回',
    config: {
      fields: [
        {
          label: '重排结果列表',
          value: 'result_list'
        },
        {
          label: '重排结果',
          value: 'result'
        }
      ]
    }
  }
}
export const formNode = {
  type: WorkflowType.FormNode,
  text: '在问答过程中用于收集用户信息，可以根据收集到表单数据执行后续流程',
  label: '表单收集',
  height: 252,
  properties: {
    width: 600,
    stepName: '表单收集',
    node_data: {
      is_result: true,
      form_field_list: [],
      form_content_format: `你好，请先填写下面表单内容：
{{form}}
填写后请点击【提交】按钮进行提交。`
    },
    config: {
      fields: [
        {
          label: '表单全部内容',
          value: 'form_data'
        }
      ]
    }
  }
}
export const documentExtractNode = {
  type: WorkflowType.DocumentExtractNode,
  text: '提取文档中的内容',
  label: '文档内容提取',
  height: 252,
  properties: {
    stepName: '文档内容提取',
    config: {
      fields: [
        {
          label: '文档内容',
          value: 'content'
        }
      ]
    }
  }
}
export const imageUnderstandNode = {
  type: WorkflowType.ImageUnderstandNode,
  text: '识别出图片中的对象、场景等信息回答用户问题',
  label: '图片理解',
  height: 252,
  properties: {
    stepName: '图片理解',
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

export const imageGenerateNode = {
  type: WorkflowType.ImageGenerateNode,
  text: '根据提供的文本内容生成图片',
  label: '图片生成',
  height: 252,
  properties: {
    stepName: '图片生成',
    config: {
      fields: [
        {
          label: 'AI 回答内容',
          value: 'answer'
        },
        {
          label: '图片',
          value: 'image'
        }
      ]
    }
  }
}

export const speechToTextNode = {
  type: WorkflowType.SpeechToTextNode,
  text: '将音频通过语音识别模型转换为文本',
  label: '语音转文本',
  height: 252,
  properties: {
    stepName: '语音转文本',
    config: {
      fields: [
        {
          label: '结果',
          value: 'result'
        }
      ]
    }
  }
}
export const textToSpeechNode = {
  type: WorkflowType.TextToSpeechNode,
  text: '将文本通过语音合成模型转换为音频',
  label: '文本转语音',
  height: 252,
  properties: {
    stepName: '文本转语音',
    config: {
      fields: [
        {
          label: '结果',
          value: 'result'
        }
      ]
    }
  }
}
export const menuNodes = [
  aiChatNode,
  imageUnderstandNode,
  imageGenerateNode,
  searchDatasetNode,
  rerankerNode,
  conditionNode,
  replyNode,
  formNode,
  questionNode,
  documentExtractNode,
  speechToTextNode,
  textToSpeechNode
]

/**
 * 自定义函数配置数据
 */
export const functionNode = {
  type: WorkflowType.FunctionLibCustom,
  text: '通过执行自定义脚本，实现数据处理',
  label: '自定义函数',
  height: 260,
  properties: {
    stepName: '自定义函数',
    config: {
      fields: [
        {
          label: '结果',
          value: 'result'
        }
      ]
    }
  }
}
export const functionLibNode = {
  type: WorkflowType.FunctionLib,
  text: '通过执行自定义脚本，实现数据处理',
  label: '自定义函数',
  height: 170,
  properties: {
    stepName: '自定义函数',
    config: {
      fields: [
        {
          label: '结果',
          value: 'result'
        }
      ]
    }
  }
}

export const applicationNode = {
  type: WorkflowType.Application,
  text: '应用节点',
  label: '应用节点',
  height: 260,
  properties: {
    stepName: '应用节点',
    config: {
      fields: [
        {
          label: '结果',
          value: 'result'
        }
      ]
    }
  }
}

export const compareList = [
  { value: 'is_null', label: '为空' },
  { value: 'is_not_null', label: '不为空' },
  { value: 'contain', label: '包含' },
  { value: 'not_contain', label: '不包含' },
  { value: 'eq', label: '等于' },
  { value: 'ge', label: '大于等于' },
  { value: 'gt', label: '大于' },
  { value: 'le', label: '小于等于' },
  { value: 'lt', label: '小于' },
  { value: 'len_eq', label: '长度等于' },
  { value: 'len_ge', label: '长度大于等于' },
  { value: 'len_gt', label: '长度大于' },
  { value: 'len_le', label: '长度小于等于' },
  { value: 'len_lt', label: '长度小于' }
]

export const nodeDict: any = {
  [WorkflowType.AiChat]: aiChatNode,
  [WorkflowType.SearchDataset]: searchDatasetNode,
  [WorkflowType.Question]: questionNode,
  [WorkflowType.Condition]: conditionNode,
  [WorkflowType.Base]: baseNode,
  [WorkflowType.Start]: startNode,
  [WorkflowType.Reply]: replyNode,
  [WorkflowType.FunctionLib]: functionLibNode,
  [WorkflowType.FunctionLibCustom]: functionNode,
  [WorkflowType.RrerankerNode]: rerankerNode,
  [WorkflowType.FormNode]: formNode,
  [WorkflowType.Application]: applicationNode,
  [WorkflowType.DocumentExtractNode]: documentExtractNode,
  [WorkflowType.ImageUnderstandNode]: imageUnderstandNode,
  [WorkflowType.TextToSpeechNode]: textToSpeechNode,
  [WorkflowType.SpeechToTextNode]: speechToTextNode,
  [WorkflowType.ImageGenerateNode]: imageGenerateNode
}
export function isWorkFlow(type: string | undefined) {
  return type === 'WORK_FLOW'
}

export function isLastNode(nodeModel: any) {
  const incoming = nodeModel.graphModel.getNodeIncomingNode(nodeModel.id)
  const outcomming = nodeModel.graphModel.getNodeOutgoingNode(nodeModel.id)
  if (incoming.length > 0 && outcomming.length === 0) {
    return true
  } else {
    return false
  }
}
