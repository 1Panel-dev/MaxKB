import { WorkflowType } from '@/enums/workflow'
import { t } from '@/locales'

export const startNode = {
  id: WorkflowType.Start,
  type: WorkflowType.Start,
  x: 480,
  y: 3340,
  properties: {
    height: 364,
    stepName: t('views.applicationWorkflow.nodes.startNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.startNode.question'),
          value: 'question'
        }
      ],
      globalFields: [
        { label: t('views.applicationWorkflow.nodes.startNode.currentTime'), value: 'time' },
        {
          label: t('views.application.applicationForm.form.historyRecord.label'),
          value: 'history_context'
        },
        {
          label: t('chat.chatId'),
          value: 'chat_id'
        }
      ]
    },
    fields: [{ label: t('views.applicationWorkflow.nodes.startNode.question'), value: 'question' }],
    globalFields: [
      { label: t('views.applicationWorkflow.nodes.startNode.currentTime'), value: 'time' }
    ],
    showNode: true
  }
}
export const baseNode = {
  id: WorkflowType.Base,
  type: WorkflowType.Base,
  x: 360,
  y: 2761.3875,
  text: '',
  properties: {
    height: 728.375,
    stepName: t('views.applicationWorkflow.nodes.baseNode.label'),
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      // @ts-ignore
      prologue: t('views.application.applicationForm.form.defaultPrologue'),
      tts_type: 'BROWSER'
    },
    config: {},
    showNode: true,
    user_input_config: { title: t('chat.userInput') },
    user_input_field_list: []
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
  text: t('views.applicationWorkflow.nodes.aiChatNode.text'),
  label: t('views.applicationWorkflow.nodes.aiChatNode.label'),
  height: 340,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.aiChatNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.aiChatNode.answer'),
          value: 'answer'
        },
        {
          label: t('views.applicationWorkflow.nodes.aiChatNode.think'),
          value: 'reasoning_content'
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
  text: t('views.applicationWorkflow.nodes.searchDatasetNode.text'),
  label: t('views.applicationWorkflow.nodes.searchDatasetNode.label'),
  height: 355,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.searchDatasetNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.searchDatasetNode.paragraph_list'),
          value: 'paragraph_list'
        },
        {
          label: t('views.applicationWorkflow.nodes.searchDatasetNode.is_hit_handling_method_list'),
          value: 'is_hit_handling_method_list'
        },
        {
          label: t('views.applicationWorkflow.nodes.searchDatasetNode.result'),
          value: 'data'
        },
        {
          label: t('views.applicationWorkflow.nodes.searchDatasetNode.directly_return'),
          value: 'directly_return'
        }
      ]
    }
  }
}
export const questionNode = {
  type: WorkflowType.Question,
  text: t('views.applicationWorkflow.nodes.questionNode.text'),
  label: t('views.applicationWorkflow.nodes.questionNode.label'),
  height: 345,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.questionNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.questionNode.result'),
          value: 'answer'
        }
      ]
    }
  }
}
export const conditionNode = {
  type: WorkflowType.Condition,
  text: t('views.applicationWorkflow.nodes.conditionNode.text'),
  label: t('views.applicationWorkflow.nodes.conditionNode.label'),
  height: 175,
  properties: {
    width: 600,
    stepName: t('views.applicationWorkflow.nodes.conditionNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.conditionNode.branch_name'),
          value: 'branch_name'
        }
      ]
    }
  }
}
export const replyNode = {
  type: WorkflowType.Reply,
  text: t('views.applicationWorkflow.nodes.replyNode.text'),
  label: t('views.applicationWorkflow.nodes.replyNode.label'),
  height: 210,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.replyNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.replyNode.content'),
          value: 'answer'
        }
      ]
    }
  }
}
export const rerankerNode = {
  type: WorkflowType.RrerankerNode,
  text: t('views.applicationWorkflow.nodes.rerankerNode.text'),
  label: t('views.applicationWorkflow.nodes.rerankerNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.rerankerNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.rerankerNode.result_list'),
          value: 'result_list'
        },
        {
          label: t('views.applicationWorkflow.nodes.rerankerNode.result'),
          value: 'result'
        }
      ]
    }
  }
}
export const formNode = {
  type: WorkflowType.FormNode,
  text: t('views.applicationWorkflow.nodes.formNode.text'),
  label: t('views.applicationWorkflow.nodes.formNode.label'),
  height: 252,
  properties: {
    width: 600,
    stepName: t('views.applicationWorkflow.nodes.formNode.label'),
    node_data: {
      is_result: true,
      form_field_list: [],
      form_content_format: `${t('views.applicationWorkflow.nodes.formNode.form_content_format1')}
{{form}}
${t('views.applicationWorkflow.nodes.formNode.form_content_format2')}`
    },
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.formNode.form_data'),
          value: 'form_data'
        }
      ]
    }
  }
}
export const documentExtractNode = {
  type: WorkflowType.DocumentExtractNode,
  text: t('views.applicationWorkflow.nodes.documentExtractNode.text'),
  label: t('views.applicationWorkflow.nodes.documentExtractNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.documentExtractNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.documentExtractNode.content'),
          value: 'content'
        }
      ]
    }
  }
}
export const imageUnderstandNode = {
  type: WorkflowType.ImageUnderstandNode,
  text: t('views.applicationWorkflow.nodes.imageUnderstandNode.text'),
  label: t('views.applicationWorkflow.nodes.imageUnderstandNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.imageUnderstandNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.imageUnderstandNode.answer'),
          value: 'answer'
        }
      ]
    }
  }
}

export const variableAssignNode = {
  type: WorkflowType.VariableAssignNode,
  text: t('views.applicationWorkflow.nodes.variableAssignNode.text'),
  label: t('views.applicationWorkflow.nodes.variableAssignNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.variableAssignNode.label'),
    config: {}
  }
}

export const mcpNode = {
  type: WorkflowType.McpNode,
  text: t('views.applicationWorkflow.nodes.mcpNode.text'),
  label: t('views.applicationWorkflow.nodes.mcpNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.mcpNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result'
        }
      ]
    }
  }
}

export const imageGenerateNode = {
  type: WorkflowType.ImageGenerateNode,
  text: t('views.applicationWorkflow.nodes.imageGenerateNode.text'),
  label: t('views.applicationWorkflow.nodes.imageGenerateNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.imageGenerateNode.label'),
    config: {
      fields: [
        {
          label: t('views.applicationWorkflow.nodes.imageGenerateNode.answer'),
          value: 'answer'
        },
        {
          label: t('common.fileUpload.image'),
          value: 'image'
        }
      ]
    }
  }
}

export const speechToTextNode = {
  type: WorkflowType.SpeechToTextNode,
  text: t('views.applicationWorkflow.nodes.speechToTextNode.text'),
  label: t('views.applicationWorkflow.nodes.speechToTextNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.speechToTextNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result'
        }
      ]
    }
  }
}
export const textToSpeechNode = {
  type: WorkflowType.TextToSpeechNode,
  text: t('views.applicationWorkflow.nodes.textToSpeechNode.text'),
  label: t('views.applicationWorkflow.nodes.textToSpeechNode.label'),
  height: 252,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.textToSpeechNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
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
  textToSpeechNode,
  variableAssignNode,
  mcpNode
]

/**
 * 自定义函数配置数据
 */
export const functionNode = {
  type: WorkflowType.FunctionLibCustom,
  text: t('views.applicationWorkflow.nodes.functionNode.text'),
  label: t('views.applicationWorkflow.nodes.functionNode.label'),
  height: 260,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.functionNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result'
        }
      ]
    }
  }
}
export const functionLibNode = {
  type: WorkflowType.FunctionLib,
  text: t('views.applicationWorkflow.nodes.functionNode.text'),
  label: t('views.applicationWorkflow.nodes.functionNode.label'),
  height: 170,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.functionNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result'
        }
      ]
    }
  }
}

export const applicationNode = {
  type: WorkflowType.Application,
  text: t('views.applicationWorkflow.nodes.applicationNode.label'),
  label: t('views.applicationWorkflow.nodes.applicationNode.label'),
  height: 260,
  properties: {
    stepName: t('views.applicationWorkflow.nodes.applicationNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result'
        }
      ]
    }
  }
}

export const compareList = [
  { value: 'is_null', label: t('views.applicationWorkflow.compare.is_null') },
  { value: 'is_not_null', label: t('views.applicationWorkflow.compare.is_not_null') },
  { value: 'contain', label: t('views.applicationWorkflow.compare.contain') },
  { value: 'not_contain', label: t('views.applicationWorkflow.compare.not_contain') },
  { value: 'eq', label: t('views.applicationWorkflow.compare.eq') },
  { value: 'ge', label: t('views.applicationWorkflow.compare.ge') },
  { value: 'gt', label: t('views.applicationWorkflow.compare.gt') },
  { value: 'le', label: t('views.applicationWorkflow.compare.le') },
  { value: 'lt', label: t('views.applicationWorkflow.compare.lt') },
  { value: 'len_eq', label: t('views.applicationWorkflow.compare.len_eq') },
  { value: 'len_ge', label: t('views.applicationWorkflow.compare.len_ge') },
  { value: 'len_gt', label: t('views.applicationWorkflow.compare.len_gt') },
  { value: 'len_le', label: t('views.applicationWorkflow.compare.len_le') },
  { value: 'len_lt', label: t('views.applicationWorkflow.compare.len_lt') },
  { value: 'is_true', label: t('views.applicationWorkflow.compare.is_true') },
  { value: 'is_not_true', label: t('views.applicationWorkflow.compare.is_not_true') }
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
  [WorkflowType.ImageGenerateNode]: imageGenerateNode,
  [WorkflowType.VariableAssignNode]: variableAssignNode,
  [WorkflowType.McpNode]: mcpNode
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
