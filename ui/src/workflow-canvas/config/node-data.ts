import { computed, reactive } from 'vue'
import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'
import { t } from '@/locales'

export const startNode = reactive({
  id: WorkflowNodeType.Start,
  type: WorkflowNodeType.Start,
  x: 846,
  y: 2600,
  properties: {
    stepName: computed(() => t('workflow.start.label')),
    config: {
      fields: [{ label: computed(() => t('workflow.start.question')), value: 'question' }],
      globalFields: [
        { label: computed(() => t('workflow.start.currentTime')), value: 'time' },
        { label: computed(() => t('workflow.history.label')), value: 'history_context' },
        { label: computed(() => t('workflow.start.chatId')), value: 'aiChat_id' },
        { label: computed(() => t('workflow.start.chatUserId')), value: 'chat_user_id' },
        { label: computed(() => t('workflow.start.chatUserType')), value: 'chat_user_type' },
        { label: computed(() => t('workflow.start.chatUserGroup')), value: 'chat_user_group' },
        { label: computed(() => t('workflow.start.chatUser')), value: 'chat_user' },
      ],
    },
    showNode: true,
  },
})

export const baseNode = reactive({
  id: WorkflowNodeType.Base,
  type: WorkflowNodeType.Base,
  x: 360,
  y: 2600,
  text: '',
  properties: {
    stepName: computed(() => t('common.labels.basicInfo')),
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      prologue: computed(() => t('application.prologue.defaultValue')),
      tts_type: 'BROWSER',
      stt_model_id_type: 'default',
      long_term_model_id_type: 'default',
    },
    config: {},
    showNode: true,
    user_input_config: { title: computed(() => t('workflow.userInput.title')) },
    user_input_field_list: [],
  },
})

export const knowledgeBaseNode = reactive({
  id: WorkflowNodeType.KnowledgeBase,
  type: WorkflowNodeType.KnowledgeBase,
  x: 360,
  y: 2600,
  text: '',
  properties: {
    stepName: computed(() => t('common.labels.basicInfo')),
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      prologue: computed(() => t('application.prologue.defaultValue')),
      tts_type: 'BROWSER',
    },
    config: {},
    showNode: true,
    user_input_config: { title: computed(() => t('workflow.userInput.title')) },
    user_input_field_list: [],
  },
})

export const toolBaseNode = reactive({
  id: WorkflowNodeType.ToolBaseNode,
  type: WorkflowNodeType.ToolBaseNode,
  x: 360,
  y: 2600,
  text: '',
  properties: {
    stepName: computed(() => t('common.labels.basicInfo')),
    input_field_list: [],
    node_data: {},
    config: {},
    showNode: true,
    user_input_config: { title: computed(() => t('workflow.userInput.title')) },
    user_input_field_list: [],
  },
})

export const toolStartNode = reactive({
  id: WorkflowNodeType.ToolStartNode,
  type: WorkflowNodeType.ToolStartNode,
  x: 846,
  y: 2600,
  text: '',
  properties: {
    stepName: computed(() => t('workflow.start.label')),
    input_field_list: [],
    node_data: {},
    config: {},
    showNode: true,
    user_input_config: { title: computed(() => t('workflow.userInput.title')) },
    user_input_field_list: [],
  },
})

// 以上是默认基础节点

/* ai对话节点配置数据 */
export const aiChatNode = reactive({
  type: WorkflowNodeType.AiChat,
  text: computed(() => t('workflow.aiChat.description')),
  label: computed(() => t('workflow.aiChat.label')),
  properties: {
    stepName: computed(() => t('workflow.aiChat.label')),
    config: {
      fields: [
        { label: computed(() => `AI ${t('workflow.answer.label')}`), value: 'answer' },
        { label: computed(() => t('workflow.thinking.process')), value: 'reasoning_content' },
        { label: computed(() => t('workflow.history.label')), value: 'history_message' },
      ],
    },
  },
})

/* LLM 节点配置数据 */
export const llmNode = reactive({
  type: WorkflowNodeType.Llm,
  text: computed(() => t('workflow.llm.description')),
  label: computed(() => t('workflow.llm.label')),
  properties: {
    stepName: computed(() => t('workflow.llm.label')),
    config: {
      fields: [
        { label: computed(() => t('workflow.answer.label')), value: 'content' },
        { label: computed(() => t('workflow.thinking.process')), value: 'reasoning_content' },
        { label: computed(() => t('workflow.llm.reasoningKey')), value: 'reasoning_key' },
        { label: computed(() => t('workflow.llm.refusal')), value: 'refusal' },
        { label: computed(() => t('workflow.llm.isRefusal')), value: 'is_refusal' },
        { label: computed(() => t('workflow.llm.usage')), value: 'usage' },
        { label: computed(() => t('workflow.llm.toolCalls')), value: 'tool_calls' },
        { label: computed(() => t('workflow.llm.finishReason')), value: 'finish_reason' },
      ],
    },
  },
})

/* 意图识别节点配置数据 */
export const intentNode = reactive({
  type: WorkflowNodeType.IntentNode,
  text: computed(() => t('workflow.intent.description')),
  label: computed(() => t('workflow.intent.label')),
  properties: {
    stepName: computed(() => t('workflow.intent.label')),
    config: {
      fields: [
        { label: computed(() => t('workflow.intent.category')), value: 'category' },
        { label: computed(() => t('workflow.intent.reason')), value: 'reason' },
      ],
    },
  },
})

/* 语音转文本节点 */
export const speechToTextNode = reactive({
  type: WorkflowNodeType.SpeechToTextNode,
  text: computed(() => t('workflow.speechToText.description')),
  label: computed(() => t('workflow.speechToText.label')),
  properties: {
    stepName: computed(() => t('workflow.speechToText.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/* 文本转语音节点 */
export const textToSpeechNode = reactive({
  type: WorkflowNodeType.TextToSpeechNode,
  text: computed(() => t('workflow.textToSpeech.description')),
  label: computed(() => t('workflow.textToSpeech.label')),
  properties: {
    stepName: computed(() => t('workflow.textToSpeech.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/* 图片生成节点 */
export const imageGenerateNode = reactive({
  type: WorkflowNodeType.ImageGenerateNode,
  text: computed(() => t('workflow.imageGenerate.description')),
  label: computed(() => t('workflow.imageGenerate.label')),
  properties: {
    stepName: computed(() => t('workflow.imageGenerate.label')),
    config: {
      fields: [
        { label: computed(() => `AI ${t('workflow.answer.label')}`), value: 'answer' },
        { label: computed(() => t('upload.types.image')), value: 'image' },
      ],
    },
  },
})

/* 图生视频节点 */
export const imageToVideoNode = reactive({
  type: WorkflowNodeType.ImageToVideoGenerateNode,
  text: computed(() => t('workflow.imageToVideo.description')),
  label: computed(() => t('workflow.imageToVideo.label')),
  properties: {
    stepName: computed(() => t('workflow.imageToVideo.label')),
    config: { fields: [{ label: computed(() => t('upload.types.video')), value: 'video' }] },
  },
})

/* 文生视频节点 */
export const textToVideoNode = reactive({
  type: WorkflowNodeType.TextToVideoGenerateNode,
  text: computed(() => t('workflow.textToVideo.description')),
  label: computed(() => t('workflow.textToVideo.label')),
  properties: {
    stepName: computed(() => t('workflow.textToVideo.label')),
    config: { fields: [{ label: computed(() => t('upload.types.video')), value: 'video' }] },
  },
})

/* 图片理解节点 */
export const imageUnderstandNode = reactive({
  type: WorkflowNodeType.ImageUnderstandNode,
  text: computed(() => t('workflow.imageUnderstand.description')),
  label: computed(() => t('workflow.imageUnderstand.label')),
  properties: {
    stepName: computed(() => t('workflow.imageUnderstand.label')),
    config: { fields: [{ label: computed(() => `AI ${t('workflow.answer.label')}`), value: 'answer' }] },
  },
})

/* 视频理解节点 */
export const videoUnderstandNode = reactive({
  type: WorkflowNodeType.VideoUnderstandNode,
  text: computed(() => t('workflow.videoUnderstand.description')),
  label: computed(() => t('workflow.videoUnderstand.label')),
  properties: {
    stepName: computed(() => t('workflow.videoUnderstand.label')),
    config: { fields: [{ label: computed(() => `AI ${t('workflow.answer.label')}`), value: 'answer' }] },
  },
})

/* 问题优化节点 */
export const questionNode = reactive({
  type: WorkflowNodeType.Question,
  text: computed(() => t('workflow.questionOptimization.description')),
  label: computed(() => t('workflow.questionOptimization.label')),
  properties: {
    stepName: computed(() => t('workflow.questionOptimization.label')),
    config: { fields: [{ label: computed(() => t('workflow.questionOptimization.result')), value: 'answer' }] },
  },
})

/* 指定回复 */
export const replyNode = reactive({
  type: WorkflowNodeType.Reply,
  text: computed(() => t('workflow.reply.description')),
  label: computed(() => t('workflow.reply.label')),
  properties: {
    stepName: computed(() => t('workflow.reply.label')),
    config: { fields: [{ label: computed(() => t('workflow.reply.content.label')), value: 'answer' }] },
  },
})

/* 判断器 */
export const conditionNode = reactive({
  type: WorkflowNodeType.Condition,
  text: computed(() => t('workflow.condition.description')),
  label: computed(() => t('workflow.condition.label')),
  properties: {
    stepName: computed(() => t('workflow.condition.label')),
    config: { fields: [{ label: computed(() => t('workflow.condition.branchName')), value: 'branch_name' }] },
  },
})

/* 表单收集 */
export const formNode = reactive({
  type: WorkflowNodeType.FormNode,
  text: computed(() => t('workflow.form.description')),
  label: computed(() => t('workflow.form.label')),
  properties: {
    stepName: computed(() => t('workflow.form.label')),
    node_data: {
      is_result: true,
      form_field_list: [],
      form_content_format: computed(() => t('workflow.form.defaultContent', { form: '{{form}}' })),
    },
    config: { fields: [{ label: computed(() => t('workflow.form.formData')), value: 'form_data' }] },
  },
})

/* 变量赋值 */
export const variableAssignNode = reactive({
  type: WorkflowNodeType.VariableAssignNode,
  text: computed(() => t('workflow.variableAssign.description')),
  label: computed(() => t('workflow.variableAssign.label')),
  properties: { stepName: computed(() => t('workflow.variableAssign.label')), config: {} },
})

/* 变量聚合 */
export const variableAggregationNode = reactive({
  type: WorkflowNodeType.VariableAggregationNode,
  text: computed(() => t('workflow.variableAggregation.description')),
  label: computed(() => t('workflow.variableAggregation.label')),
  // 分支汇合：各分支互斥执行，需“任一”前置完成即执行，否则会一直等待未执行的分支
  properties: { stepName: computed(() => t('workflow.variableAggregation.label')), condition: 'OR', config: { fields: [] } },
})

/* 变量拆分 */
export const variableSplittingNode = reactive({
  type: WorkflowNodeType.VariableSplittingNode,
  text: computed(() => t('workflow.variableSplitting.description')),
  label: computed(() => t('workflow.variableSplitting.label')),
  properties: {
    stepName: computed(() => t('workflow.variableSplitting.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/* 参数提取 */
export const parameterExtractionNode = reactive({
  type: WorkflowNodeType.ParameterExtractionNode,
  text: computed(() => t('workflow.parameterExtraction.description')),
  label: computed(() => t('workflow.parameterExtraction.label')),
  properties: {
    stepName: computed(() => t('workflow.parameterExtraction.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/* 知识库检索 */
export const searchKnowledgeNode = reactive({
  type: WorkflowNodeType.SearchKnowledge,
  text: computed(() => t('workflow.searchKnowledge.description')),
  label: computed(() => t('workflow.searchKnowledge.label')),
  properties: {
    stepName: computed(() => t('workflow.searchKnowledge.label')),
    config: {
      fields: [
        { label: computed(() => t('workflow.searchKnowledge.segmentList')), value: 'paragraph_list' },
        { label: computed(() => t('workflow.searchKnowledge.directAnswerSegments')), value: 'is_hit_handling_method_list' },
        { label: computed(() => t('workflow.searchKnowledge.result')), value: 'data' },
        { label: computed(() => t('workflow.searchKnowledge.directAnswerContent')), value: 'directly_return' },
      ],
    },
  },
})

/* 文档标签检索 */
export const searchDocumentNode = reactive({
  type: WorkflowNodeType.SearchDocument,
  text: computed(() => t('workflow.searchDocument.description')),
  label: computed(() => t('workflow.searchDocument.label')),
  properties: {
    stepName: computed(() => t('workflow.searchDocument.label')),
    config: {
      fields: [
        { label: computed(() => t('workflow.searchDocument.knowledgeList')), value: 'knowledge_list' },
        { label: computed(() => t('workflow.searchDocument.documentList')), value: 'document_list' },
      ],
    },
  },
})

/* 文档内容提取 */
export const documentExtractNode = reactive({
  type: WorkflowNodeType.DocumentExtractNode,
  text: computed(() => t('workflow.documentExtract.description')),
  label: computed(() => t('workflow.documentExtract.label')),
  properties: {
    stepName: computed(() => t('workflow.documentExtract.label')),
    config: {
      fields: [
        { label: computed(() => t('workflow.documentExtract.content')), value: 'content' },
        { label: computed(() => t('workflow.documentExtract.documentList')), value: 'document_list' },
      ],
    },
  },
})

/* 多路召回 */
export const rerankerNode = reactive({
  type: WorkflowNodeType.RerankerNode,
  text: computed(() => t('workflow.reranker.description')),
  label: computed(() => t('workflow.reranker.label')),
  properties: {
    stepName: computed(() => t('workflow.reranker.label')),
    config: {
      fields: [
        { label: computed(() => t('workflow.reranker.resultList')), value: 'result_list' },
        { label: computed(() => t('workflow.reranker.result')), value: 'result' },
        { label: computed(() => t('workflow.reranker.directAnswerSegments')), value: 'is_hit_handling_method_list' },
      ],
    },
  },
})

/* MCP 调用 */
export const mcpNode = reactive({
  type: WorkflowNodeType.McpNode,
  text: computed(() => t('workflow.mcp.description')),
  label: computed(() => t('workflow.mcp.label')),
  properties: {
    stepName: computed(() => t('workflow.mcp.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/* 自定义工具 */
export const toolCustomNode = reactive({
  type: WorkflowNodeType.ToolLibCustom,
  text: computed(() => t('workflow.customTool.description')),
  label: computed(() => t('workflow.customTool.label')),
  properties: {
    stepName: computed(() => t('workflow.customTool.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/* 智能体节点 */
export const applicationNode = reactive({
  type: WorkflowNodeType.Application,
  text: computed(() => t('workflow.application.label')),
  label: computed(() => t('workflow.application.label')),
  properties: {
    stepName: computed(() => t('workflow.application.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/**
 * 工具配置数据
 */
export const toolLibNode = reactive({
  type: WorkflowNodeType.ToolLib,
  text: computed(() => t('workflow.tool.label')),
  label: computed(() => t('workflow.tool.label')),
  properties: {
    stepName: computed(() => t('workflow.tool.label')),
    config: { fields: [{ label: computed(() => t('workflow.node.result')), value: 'result' }] },
  },
})

/**
 * 工作流工具配置数据
 */
export const toolWorkflowLibNode = reactive({
  type: WorkflowNodeType.ToolWorkflowLib,
  text: computed(() => t('workflow.toolWorkflow.label')),
  label: computed(() => t('workflow.toolWorkflow.label')),
  properties: { stepName: computed(() => t('workflow.toolWorkflow.label')), config: { fields: [] } },
})

/* 循环节点 */

export const loopNode = reactive({
  type: WorkflowNodeType.LoopNode,
  visible: false,
  text: computed(() => t('workflow.loop.description')),
  label: computed(() => t('workflow.loop.label')),
  properties: {
    stepName: computed(() => t('workflow.loop.label')),
    workflow: {
      edges: [],
      nodes: [
        {
          x: 480,
          y: 200,
          id: 'loop-start-node',
          type: 'loop-start-node',
          properties: {
            config: {
              // 循环引擎内置的输出参数（index/item），只读展示，用户不可增删改
              fields: [
                { label: computed(() => t('workflow.loopStart.index')), value: 'index' },
                { label: computed(() => t('workflow.loopStart.item')), value: 'item' },
              ],
              globalFields: [],
            },
            fields: [],
            showNode: true,
            stepName: computed(() => t('workflow.loopStart.label')),
            globalFields: [],
          },
        },
      ],
    },
    config: { fields: [] },
  },
})

export const loopStartNode = reactive({
  id: WorkflowNodeType.LoopStartNode,
  type: WorkflowNodeType.LoopStartNode,
  x: 480,
  y: 200,
  properties: {
    stepName: computed(() => t('workflow.loopStart.label')),
    config: {
      // 循环引擎内置的输出参数（index/item），只读展示，用户不可增删改
      fields: [
        { label: computed(() => t('workflow.loopStart.index')), value: 'index' },
        { label: computed(() => t('workflow.loopStart.item')), value: 'item' },
      ],
      globalFields: [],
    },
    showNode: true,
  },
})

export const loopBodyNode = reactive({
  type: WorkflowNodeType.LoopBodyNode,
  text: computed(() => t('workflow.loopBody.label')),
  label: computed(() => t('workflow.loopBody.label')),
  height: 1080,

  properties: { width: 1920, stepName: computed(() => t('workflow.loopBody.label')), config: { fields: [] } },
})

export const loopContinueNode = reactive({
  type: WorkflowNodeType.LoopContinueNode,
  text: computed(() => t('workflow.loopContinue.description')),
  label: computed(() => t('workflow.loopContinue.label')),
  properties: { width: 600, stepName: computed(() => t('workflow.loopContinue.label')), config: { fields: [] } },
})

export const loopBreakNode = reactive({
  type: WorkflowNodeType.LoopBreakNode,
  text: computed(() => t('workflow.loopBreak.description')),
  label: computed(() => t('workflow.loopBreak.label')),
  properties: { width: 600, stepName: computed(() => t('workflow.loopBreak.label')), config: { fields: [] } },
})

/* 文档分段 */
export const documentSplitNode = reactive({
  type: WorkflowNodeType.DocumentSplitNode,
  text: computed(() => t('workflow.documentSplit.description')),
  label: computed(() => t('workflow.documentSplit.label')),
  properties: {
    stepName: computed(() => t('workflow.documentSplit.label')),
    config: { fields: [{ label: computed(() => t('workflow.documentSplit.segmentList')), value: 'paragraph_list' }] },
  },
})

export const dataSourceLocalNode = reactive({
  type: WorkflowNodeType.DataSourceLocalNode,
  x: 360,
  y: 2761.3875,
  text: computed(() => t('workflow.localFile.description')),
  label: computed(() => t('workflow.localFile.label')),
  properties: {
    kind: WorkflowKind.DataSource,
    height: 728.375,
    stepName: computed(() => t('workflow.localFile.label')),
    input_field_list: [],
    config: { fields: [{ label: computed(() => t('workflow.localFile.fileList')), value: 'file_list' }] },
    showNode: true,
    user_input_config: {},
    user_input_field_list: [],
  },
})

export const dataSourceWebNode = reactive({
  id: WorkflowNodeType.DataSourceWebNode,
  type: WorkflowNodeType.DataSourceWebNode,
  x: 360,
  y: 2761.3875,
  text: computed(() => t('workflow.webSource.description')),
  label: computed(() => t('workflow.webSource.label')),
  properties: {
    kind: WorkflowKind.DataSource,
    height: 180,
    stepName: computed(() => t('workflow.webSource.label')),
    config: { fields: [{ label: computed(() => t('workflow.webSource.documentList')), value: 'document_list' }] },
  },
})

export const knowledgeWriteNode = reactive({
  type: WorkflowNodeType.KnowledgeWriteNode,
  text: computed(() => t('workflow.knowledgeWrite.description')),
  label: computed(() => t('workflow.knowledgeWrite.label')),
  height: 100,
  properties: { stepName: computed(() => t('workflow.knowledgeWrite.label')), config: { fields: [] } },
})
