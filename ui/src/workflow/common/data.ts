import { WorkflowKind } from './../../enums/application'
import { WorkflowType, WorkflowMode } from '@/enums/application'
import { t } from '@/locales'

export const startNode = {
  id: WorkflowType.Start,
  type: WorkflowType.Start,
  x: 480,
  y: 3340,
  properties: {
    height: 364,
    stepName: t('workflow.nodes.startNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.startNode.question'),
          value: 'question',
        },
      ],
      globalFields: [
        { label: t('workflow.nodes.startNode.currentTime'), value: 'time' },
        {
          label: t('views.application.form.historyRecord.label'),
          value: 'history_context',
        },
        {
          label: t('chat.chatId'),
          value: 'chat_id',
        },
      ],
    },
    fields: [{ label: t('workflow.nodes.startNode.question'), value: 'question' }],
    globalFields: [{ label: t('workflow.nodes.startNode.currentTime'), value: 'time' }],
    showNode: true,
  },
}
export const baseNode = {
  id: WorkflowType.Base,
  type: WorkflowType.Base,
  x: 360,
  y: 2761.3875,
  text: '',
  properties: {
    height: 728.375,
    stepName: t('workflow.nodes.baseNode.label'),
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      prologue: t('views.application.form.defaultPrologue'),
      tts_type: 'BROWSER',
    },
    config: {},
    showNode: true,
    user_input_config: { title: t('chat.userInput') },
    user_input_field_list: [],
  },
}
export const knowledgeBaseNode = {
  id: WorkflowType.KnowledgeBase,
  type: WorkflowType.KnowledgeBase,
  x: 360,
  y: 2761.3875,
  text: '',
  properties: {
    height: 728.375,
    stepName: t('workflow.nodes.baseNode.label'),
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      prologue: t('views.application.form.defaultPrologue'),
      tts_type: 'BROWSER',
    },
    config: {},
    showNode: true,
    user_input_config: { title: t('chat.userInput') },
    user_input_field_list: [],
  },
}
export const dataSourceLocalNode = {
  type: WorkflowType.DataSourceLocalNode,
  x: 360,
  y: 2761.3875,
  text: t('workflow.nodes.dataSourceLocalNode.text'),
  label: t('workflow.nodes.dataSourceLocalNode.label'),
  properties: {
    kind: WorkflowKind.DataSource,
    height: 728.375,
    stepName: t('workflow.nodes.dataSourceLocalNode.label'),
    input_field_list: [],
    config: {
      fields: [
        {
          label: t('workflow.nodes.dataSourceLocalNode.fileList'),
          value: 'file_list',
        },
      ],
    },
    showNode: true,
    user_input_config: {},
    user_input_field_list: [],
  },
}

export const dataSourceWebNode = {
  id: WorkflowType.DataSourceWebNode,
  type: WorkflowType.DataSourceWebNode,
  x: 360,
  y: 2761.3875,
  text: t('workflow.nodes.dataSourceWebNode.text'),
  label: t('workflow.nodes.dataSourceWebNode.label'),
  properties: {
    kind: WorkflowKind.DataSource,
    height: 180,
    stepName: t('workflow.nodes.dataSourceWebNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.dataSourceWebNode.field_label'),
          value: 'document_list',
        },
      ],
    },
  },
}

export const knowledgeWriteNode = {
  type: WorkflowType.KnowledgeWriteNode,
  text: t('workflow.nodes.knowledgeWriteNode.text'),
  label: t('workflow.nodes.knowledgeWriteNode.label'),
  height: 100,
  properties: {
    stepName: t('workflow.nodes.knowledgeWriteNode.label'),
    config: {
      fields: [],
    },
  },
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
  text: t('workflow.nodes.aiChatNode.text'),
  label: t('workflow.nodes.aiChatNode.label'),
  height: 340,
  properties: {
    stepName: t('workflow.nodes.aiChatNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.aiChatNode.answer'),
          value: 'answer',
        },
        {
          label: t('workflow.nodes.aiChatNode.think'),
          value: 'reasoning_content',
        },
        {
          label: t('workflow.nodes.aiChatNode.historyMessage'),
          value: 'history_message',
        },
      ],
    },
  },
}
/**
 * 知识库检索配置数据
 */
export const searchKnowledgeNode = {
  type: WorkflowType.SearchKnowledge,
  text: t('workflow.nodes.searchKnowledgeNode.text'),
  label: t('workflow.nodes.searchKnowledgeNode.label'),
  height: 355,
  properties: {
    stepName: t('workflow.nodes.searchKnowledgeNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.searchKnowledgeNode.paragraph_list'),
          value: 'paragraph_list',
        },
        {
          label: t('workflow.nodes.searchKnowledgeNode.is_hit_handling_method_list'),
          value: 'is_hit_handling_method_list',
        },
        {
          label: t('workflow.nodes.searchKnowledgeNode.result'),
          value: 'data',
        },
        {
          label: t('workflow.nodes.searchKnowledgeNode.directly_return'),
          value: 'directly_return',
        },
      ],
    },
  },
}

/**
 * 知识库检索配置数据
 */
export const searchDocumentNode = {
  type: WorkflowType.SearchDocument,
  text: t('workflow.nodes.searchDocumentNode.text'),
  label: t('workflow.nodes.searchDocumentNode.label'),
  height: 355,
  properties: {
    width: 600,
    stepName: t('workflow.nodes.searchDocumentNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.searchDocumentNode.knowledgeList'),
          value: 'knowledge_list',
        },
        {
          label: t('workflow.nodes.searchDocumentNode.documentList'),
          value: 'document_list',
        },
      ],
    },
  },
}

export const questionNode = {
  type: WorkflowType.Question,
  text: t('workflow.nodes.questionNode.text'),
  label: t('workflow.nodes.questionNode.label'),
  height: 345,
  properties: {
    stepName: t('workflow.nodes.questionNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.questionNode.result'),
          value: 'answer',
        },
      ],
    },
  },
}
export const variableSplittingNode = {
  type: WorkflowType.VariableSplittingNode,
  text: t('workflow.nodes.variableSplittingNode.text'),
  label: t('workflow.nodes.variableSplittingNode.label'),
  height: 345,
  properties: {
    stepName: t('workflow.nodes.variableSplittingNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}

export const parameterExtractionNode = {
  type: WorkflowType.ParameterExtractionNode,
  text: t('workflow.nodes.parameterExtractionNode.text'),
  label: t('workflow.nodes.parameterExtractionNode.label'),
  height: 345,
  properties: {
    width: 430,
    stepName: t('workflow.nodes.parameterExtractionNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}

export const conditionNode = {
  type: WorkflowType.Condition,
  text: t('workflow.nodes.conditionNode.text'),
  label: t('workflow.nodes.conditionNode.label'),
  height: 175,
  properties: {
    width: 600,
    stepName: t('workflow.nodes.conditionNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.conditionNode.branch_name'),
          value: 'branch_name',
        },
      ],
    },
  },
}
export const replyNode = {
  type: WorkflowType.Reply,
  text: t('workflow.nodes.replyNode.text'),
  label: t('workflow.nodes.replyNode.label'),
  height: 210,
  properties: {
    stepName: t('workflow.nodes.replyNode.label'),
    config: {
      fields: [
        {
          label: t('common.content'),
          value: 'answer',
        },
      ],
    },
  },
}
export const rerankerNode = {
  type: WorkflowType.RerankerNode,
  text: t('workflow.nodes.rerankerNode.text'),
  label: t('workflow.nodes.rerankerNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.rerankerNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.rerankerNode.result_list'),
          value: 'result_list',
        },
        {
          label: t('workflow.nodes.rerankerNode.result'),
          value: 'result',
        },
      ],
    },
  },
}
export const formNode = {
  type: WorkflowType.FormNode,
  text: t('workflow.nodes.formNode.text'),
  label: t('workflow.nodes.formNode.label'),
  height: 252,
  properties: {
    width: 600,
    stepName: t('workflow.nodes.formNode.label'),
    node_data: {
      is_result: true,
      form_field_list: [],
      form_content_format: `${t('workflow.nodes.formNode.form_content_format1')}
{{form}}
${t('workflow.nodes.formNode.form_content_format2')}`,
    },
    config: {
      fields: [
        {
          label: t('workflow.nodes.formNode.form_data'),
          value: 'form_data',
        },
      ],
    },
  },
}
export const documentExtractNode = {
  type: WorkflowType.DocumentExtractNode,
  text: t('workflow.nodes.documentExtractNode.text'),
  label: t('workflow.nodes.documentExtractNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.documentExtractNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.documentExtractNode.content'),
          value: 'content',
        },
        {
          label: t('workflow.nodes.dataSourceWebNode.field_label'),
          value: 'document_list',
        },
      ],
    },
  },
}
export const documentSplitNode = {
  type: WorkflowType.DocumentSplitNode,
  text: t('workflow.nodes.documentSplitNode.text'),
  label: t('workflow.nodes.documentSplitNode.label'),
  height: 252,
  properties: {
    width: 500,
    stepName: t('workflow.nodes.documentSplitNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.documentSplitNode.paragraphList'),
          value: 'paragraph_list',
        },
      ],
    },
  },
}
export const imageUnderstandNode = {
  type: WorkflowType.ImageUnderstandNode,
  text: t('workflow.nodes.imageUnderstandNode.text'),
  label: t('workflow.nodes.imageUnderstandNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.imageUnderstandNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.imageUnderstandNode.answer'),
          value: 'answer',
        },
      ],
    },
  },
}

export const videoUnderstandNode = {
  type: WorkflowType.VideoUnderstandNode,
  text: t('workflow.nodes.videoUnderstandNode.text'),
  label: t('workflow.nodes.videoUnderstandNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.videoUnderstandNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.videoUnderstandNode.answer'),
          value: 'answer',
        },
      ],
    },
  },
}
export const variableAggregationNode = {
  type: WorkflowType.VariableAggregationNode,
  text: t('workflow.nodes.variableAggregationNode.text'),
  label: t('workflow.nodes.variableAggregationNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.variableAggregationNode.label'),
    config: {
      fields: [],
    },
  },
}

export const variableAssignNode = {
  type: WorkflowType.VariableAssignNode,
  text: t('workflow.nodes.variableAssignNode.text'),
  label: t('workflow.nodes.variableAssignNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.variableAssignNode.label'),
    config: {},
  },
}

export const mcpNode = {
  type: WorkflowType.McpNode,
  text: t('workflow.nodes.mcpNode.text'),
  label: t('workflow.nodes.mcpNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.mcpNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}

export const imageGenerateNode = {
  type: WorkflowType.ImageGenerateNode,
  text: t('workflow.nodes.imageGenerateNode.text'),
  label: t('workflow.nodes.imageGenerateNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.imageGenerateNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.imageGenerateNode.answer'),
          value: 'answer',
        },
        {
          label: t('common.fileUpload.image'),
          value: 'image',
        },
      ],
    },
  },
}

export const speechToTextNode = {
  type: WorkflowType.SpeechToTextNode,
  text: t('workflow.nodes.speechToTextNode.text'),
  label: t('workflow.nodes.speechToTextNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.speechToTextNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}
export const textToSpeechNode = {
  type: WorkflowType.TextToSpeechNode,
  text: t('workflow.nodes.textToSpeechNode.text'),
  label: t('workflow.nodes.textToSpeechNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.textToSpeechNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}

/**
 * 自定义工具配置数据
 */
export const toolNode = {
  type: WorkflowType.ToolLibCustom,
  text: t('workflow.nodes.toolNode.text'),
  label: t('workflow.nodes.toolNode.label'),
  height: 260,
  properties: {
    stepName: t('workflow.nodes.toolNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}

export const intentNode = {
  type: WorkflowType.IntentNode,
  text: t('workflow.nodes.intentNode.text'),
  label: t('workflow.nodes.intentNode.label'),
  height: 260,
  properties: {
    stepName: t('workflow.nodes.intentNode.label'),
    config: {
      fields: [
        {
          label: t('common.classify'),
          value: 'category',
        },
        {
          label: t('common.reason'),
          value: 'reason',
        },
      ],
    },
  },
}

export const loopStartNode = {
  id: WorkflowType.LoopStartNode,
  type: WorkflowType.LoopStartNode,
  x: 480,
  y: 3340,
  properties: {
    height: 364,
    stepName: t('workflow.nodes.loopStartNode.label'),
    config: {
      fields: [
        {
          label: t('workflow.nodes.loopStartNode.loopIndex'),
          value: 'index',
        },
        {
          label: t('workflow.nodes.loopStartNode.loopItem'),
          value: 'item',
        },
      ],
      globalFields: [],
    },
    showNode: true,
  },
}

export const loopNode = {
  type: WorkflowType.LoopNode,
  visible: false,
  text: t('workflow.nodes.loopNode.text'),
  label: t('workflow.nodes.loopNode.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.loopNode.label'),
    workflow: {
      edges: [],
      nodes: [
        {
          x: 480,
          y: 3340,
          id: 'loop-start-node',
          type: 'loop-start-node',
          properties: {
            config: {
              fields: [],
              globalFields: [],
            },
            fields: [],
            height: 361.333,
            showNode: true,
            stepName: '开始',
            globalFields: [],
          },
        },
      ],
    },
    config: {
      fields: [],
    },
  },
}

export const imageToVideoNode = {
  type: WorkflowType.ImageToVideoGenerateNode,
  text: t('workflow.nodes.imageToVideoGenerate.text'),
  label: t('workflow.nodes.imageToVideoGenerate.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.imageToVideoGenerate.label'),
    config: {
      fields: [
        {
          label: t('common.fileUpload.video'),
          value: 'video',
        },
      ],
    },
  },
}

export const loopBodyNode = {
  type: WorkflowType.LoopBodyNode,
  text: t('workflow.nodes.loopBodyNode.text'),
  label: t('workflow.nodes.loopBodyNode.label'),
  height: 1080,
  properties: {
    width: 1920,
    stepName: t('workflow.nodes.loopBodyNode.label'),
    config: {
      fields: [],
    },
  },
}
export const loopContinueNode = {
  type: WorkflowType.LoopContinueNode,
  text: t('workflow.nodes.loopContinueNode.text'),
  label: t('workflow.nodes.loopContinueNode.label'),
  height: 100,
  properties: {
    width: 600,
    stepName: t('workflow.nodes.loopContinueNode.label'),
    config: {
      fields: [],
    },
  },
}

export const textToVideoNode = {
  type: WorkflowType.TextToVideoGenerateNode,
  text: t('workflow.nodes.textToVideoGenerate.text'),
  label: t('workflow.nodes.textToVideoGenerate.label'),
  height: 252,
  properties: {
    stepName: t('workflow.nodes.textToVideoGenerate.label'),
    config: {
      fields: [
        {
          label: t('common.fileUpload.video'),
          value: 'video',
        },
      ],
    },
  },
}

export const loopBreakNode = {
  type: WorkflowType.LoopBreakNode,
  text: t('workflow.nodes.loopBreakNode.text'),
  label: t('workflow.nodes.loopBreakNode.label'),
  height: 100,
  properties: {
    width: 600,
    stepName: t('workflow.nodes.loopBreakNode.label'),
    config: {
      fields: [],
    },
  },
}

export const knowledgeMenuNodes = [
  {
    label: t('views.tool.dataSource.title'),
    list: [dataSourceLocalNode, dataSourceWebNode],
  },
  {
    label: t('views.knowledge.title'),
    list: [documentSplitNode, knowledgeWriteNode, documentExtractNode],
  },
  {
    label: t('workflow.nodes.classify.aiCapability'),
    list: [
      aiChatNode,
      intentNode,
      textToSpeechNode,
      speechToTextNode,
      imageGenerateNode,
      imageUnderstandNode,
      textToVideoNode,
      imageToVideoNode,
      videoUnderstandNode,
      questionNode,
    ],
  },

  {
    label: t('workflow.nodes.classify.businessLogic'),
    list: [conditionNode, replyNode, loopNode],
  },
  {
    label: t('workflow.nodes.classify.dataProcessing'),
    list: [
      variableAssignNode,
      variableAggregationNode,
      variableSplittingNode,
      parameterExtractionNode,
    ],
  },
  {
    label: t('workflow.nodes.classify.other'),
    list: [mcpNode, toolNode],
  },
]

export const menuNodes = [
  {
    label: t('workflow.nodes.classify.aiCapability'),
    list: [
      aiChatNode,
      intentNode,
      textToSpeechNode,
      speechToTextNode,
      imageGenerateNode,
      imageUnderstandNode,
      textToVideoNode,
      imageToVideoNode,
      videoUnderstandNode,
      questionNode,
    ],
  },
  {
    label: t('views.knowledge.title'),
    list: [
      searchKnowledgeNode,
      searchDocumentNode,
      rerankerNode,
      documentExtractNode,
      documentSplitNode,
      knowledgeWriteNode,
    ],
  },
  {
    label: t('workflow.nodes.classify.businessLogic'),
    list: [conditionNode, formNode, replyNode, loopNode],
  },
  {
    label: t('workflow.nodes.classify.dataProcessing'),
    list: [
      variableAssignNode,
      variableAggregationNode,
      variableSplittingNode,
      parameterExtractionNode,
    ],
  },
  {
    label: t('workflow.nodes.classify.other'),
    list: [mcpNode, toolNode],
  },
]
export const applicationLoopMenuNodes = [
  {
    label: t('workflow.nodes.classify.aiCapability'),
    list: [
      aiChatNode,
      intentNode,
      textToSpeechNode,
      speechToTextNode,
      imageGenerateNode,
      imageUnderstandNode,
      textToVideoNode,
      imageToVideoNode,
      videoUnderstandNode,
      questionNode,
    ],
  },
  {
    label: t('views.knowledge.title'),
    list: [searchKnowledgeNode, searchDocumentNode, rerankerNode, documentExtractNode],
  },
  {
    label: t('workflow.nodes.classify.businessLogic'),
    list: [conditionNode, formNode, replyNode, loopContinueNode, loopBreakNode],
  },
  {
    label: t('workflow.nodes.classify.dataProcessing'),
    list: [
      variableAssignNode,
      variableAggregationNode,
      variableSplittingNode,
      parameterExtractionNode,
    ],
  },
  {
    label: t('workflow.nodes.classify.other'),
    list: [mcpNode, toolNode],
  },
]
export const knowledgeLoopMenuNodes = [
  {
    label: t('views.tool.dataSource.title'),
    list: [dataSourceLocalNode, dataSourceWebNode],
  },
  {
    label: t('workflow.nodes.classify.aiCapability'),
    list: [
      aiChatNode,
      intentNode,
      textToSpeechNode,
      speechToTextNode,
      imageGenerateNode,
      imageUnderstandNode,
      textToVideoNode,
      imageToVideoNode,
      videoUnderstandNode,
      questionNode,
    ],
  },
  {
    label: t('views.knowledge.title'),
    list: [documentSplitNode, knowledgeWriteNode, documentExtractNode],
  },
  {
    label: t('workflow.nodes.classify.businessLogic'),
    list: [conditionNode, replyNode, loopContinueNode, loopBreakNode],
  },
  {
    label: t('workflow.nodes.classify.dataProcessing'),
    list: [
      variableAssignNode,
      variableAggregationNode,
      variableSplittingNode,
      parameterExtractionNode,
    ],
  },
  {
    label: t('workflow.nodes.classify.other'),
    list: [mcpNode, toolNode],
  },
]

export const getMenuNodes = (workflowMode: WorkflowMode) => {
  if (workflowMode == WorkflowMode.Application) {
    return menuNodes
  }
  if (workflowMode == WorkflowMode.ApplicationLoop) {
    return applicationLoopMenuNodes
  }
  if (workflowMode == WorkflowMode.Knowledge) {
    return knowledgeMenuNodes
  }
  if (workflowMode == WorkflowMode.KnowledgeLoop) {
    return knowledgeLoopMenuNodes
  }
}

/**
 * 工具配置数据
 */
export const toolLibNode = {
  type: WorkflowType.ToolLib,
  text: t('workflow.nodes.toolNode.text'),
  label: t('workflow.nodes.toolNode.label'),
  height: 170,
  properties: {
    stepName: t('workflow.nodes.toolNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}

export const applicationNode = {
  type: WorkflowType.Application,
  text: t('workflow.nodes.applicationNode.label'),
  label: t('workflow.nodes.applicationNode.label'),
  height: 260,
  properties: {
    stepName: t('workflow.nodes.applicationNode.label'),
    config: {
      fields: [
        {
          label: t('common.result'),
          value: 'result',
        },
      ],
    },
  },
}

export const compareList = [
  { value: 'is_null', label: t('workflow.compare.is_null') },
  { value: 'is_not_null', label: t('workflow.compare.is_not_null') },
  { value: 'contain', label: t('workflow.compare.contain') },
  { value: 'not_contain', label: t('workflow.compare.not_contain') },
  { value: 'eq', label: t('workflow.compare.eq') },
  { value: 'ge', label: t('workflow.compare.ge') },
  { value: 'gt', label: t('workflow.compare.gt') },
  { value: 'le', label: t('workflow.compare.le') },
  { value: 'lt', label: t('workflow.compare.lt') },
  { value: 'len_eq', label: t('workflow.compare.len_eq') },
  { value: 'len_ge', label: t('workflow.compare.len_ge') },
  { value: 'len_gt', label: t('workflow.compare.len_gt') },
  { value: 'len_le', label: t('workflow.compare.len_le') },
  { value: 'len_lt', label: t('workflow.compare.len_lt') },
  { value: 'is_true', label: t('workflow.compare.is_true') },
  { value: 'is_not_true', label: t('workflow.compare.is_not_true') },
  { value: 'start_with', label: 'startWith' },
  { value: 'end_with', label: 'endWith' },
]
export const nodeDict: any = {
  [WorkflowType.AiChat]: aiChatNode,
  [WorkflowType.SearchKnowledge]: searchKnowledgeNode,
  [WorkflowType.SearchDocument]: searchDocumentNode,
  [WorkflowType.Question]: questionNode,
  [WorkflowType.Condition]: conditionNode,
  [WorkflowType.Base]: baseNode,
  [WorkflowType.Start]: startNode,
  [WorkflowType.Reply]: replyNode,
  [WorkflowType.ToolLib]: toolNode,
  [WorkflowType.ToolLibCustom]: toolNode,
  [WorkflowType.RerankerNode]: rerankerNode,
  [WorkflowType.FormNode]: formNode,
  [WorkflowType.Application]: applicationNode,
  [WorkflowType.DocumentExtractNode]: documentExtractNode,
  [WorkflowType.DocumentSplitNode]: documentSplitNode,
  [WorkflowType.ImageUnderstandNode]: imageUnderstandNode,
  [WorkflowType.TextToSpeechNode]: textToSpeechNode,
  [WorkflowType.SpeechToTextNode]: speechToTextNode,
  [WorkflowType.ImageGenerateNode]: imageGenerateNode,
  [WorkflowType.VariableAssignNode]: variableAssignNode,
  [WorkflowType.McpNode]: mcpNode,
  [WorkflowType.TextToVideoGenerateNode]: textToVideoNode,
  [WorkflowType.ImageToVideoGenerateNode]: imageToVideoNode,
  [WorkflowType.IntentNode]: intentNode,
  [WorkflowType.LoopNode]: loopNode,
  [WorkflowType.LoopBodyNode]: loopBodyNode,
  [WorkflowType.LoopStartNode]: loopStartNode,
  [WorkflowType.LoopBreakNode]: loopBodyNode,
  [WorkflowType.LoopContinueNode]: loopContinueNode,
  [WorkflowType.VariableSplittingNode]: variableSplittingNode,
  [WorkflowType.VideoUnderstandNode]: videoUnderstandNode,
  [WorkflowType.ParameterExtractionNode]: parameterExtractionNode,
  [WorkflowType.VariableAggregationNode]: variableAggregationNode,
  [WorkflowType.KnowledgeBase]: knowledgeBaseNode,
  [WorkflowType.DataSourceLocalNode]: dataSourceLocalNode,
  [WorkflowType.DataSourceWebNode]: dataSourceWebNode,
  [WorkflowType.KnowledgeWriteNode]: knowledgeWriteNode,
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
