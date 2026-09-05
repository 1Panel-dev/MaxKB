import { WorkflowKind, WorkflowNodeType } from '@/workflow-canvas/types'

export const startNode = {
  id: WorkflowNodeType.Start,
  type: WorkflowNodeType.Start,
  x: 846,
  y: 2600,
  properties: {
    stepName: '开始',
    config: {
      fields: [{ label: '用户问题', value: 'question' }],
      globalFields: [
        { label: '当前时间', value: 'time' },
        { label: '历史聊天记录', value: 'history_context' },
        { label: '对话 ID', value: 'aiChat_id' },
        { label: '对话用户 ID', value: 'chat_user_id' },
        { label: '对话用户类型', value: 'chat_user_type' },
        { label: '对话用户组', value: 'chat_user_group' },
        { label: '对话用户', value: 'chat_user' },
      ],
    },
    showNode: true,
  },
}

export const baseNode = {
  id: WorkflowNodeType.Base,
  type: WorkflowNodeType.Base,
  x: 360,
  y: 2600,
  text: '',
  properties: {
    stepName: '基本信息',
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      prologue: '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务',
      tts_type: 'BROWSER',
      stt_model_id_type: 'default',
      long_term_model_id_type: 'default',
    },
    config: {},
    showNode: true,
    user_input_config: { title: '用户输入' },
    user_input_field_list: [],
  },
}

export const knowledgeBaseNode = {
  id: WorkflowNodeType.KnowledgeBase,
  type: WorkflowNodeType.KnowledgeBase,
  x: 360,
  y: 2600,
  text: '',
  properties: {
    stepName: '基本信息',
    input_field_list: [],
    node_data: {
      name: '',
      desc: '',
      prologue: '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务',
      tts_type: 'BROWSER',
    },
    config: {},
    showNode: true,
    user_input_config: { title: '用户输入' },
    user_input_field_list: [],
  },
}

export const toolBaseNode = {
  id: WorkflowNodeType.ToolBaseNode,
  type: WorkflowNodeType.ToolBaseNode,
  x: 360,
  y: 2600,
  text: '',
  properties: {
    stepName: '基本信息',
    input_field_list: [],
    node_data: {},
    config: {},
    showNode: true,
    user_input_config: { title: '用户输入' },
    user_input_field_list: [],
  },
}

export const toolStartNode = {
  id: WorkflowNodeType.ToolStartNode,
  type: WorkflowNodeType.ToolStartNode,
  x: 946,
  y: 2600,
  text: '',
  properties: {
    stepName: '开始',
    input_field_list: [],
    node_data: {},
    config: {},
    showNode: true,
    user_input_config: { title: '用户输入' },
    user_input_field_list: [],
  },
}

// 以上是默认基础节点




export const replyNode = {
  type: WorkflowNodeType.Reply,
  text: '指定回复内容，引用变量会转换为字符串进行输出',
  label: '指定回复',
  properties: { stepName: '指定回复', config: { fields: [{ label: '内容', value: 'answer' }] } },
}

/* ai对话节点配置数据 */
export const aiChatNode = {
  type: WorkflowNodeType.AiChat,
  text: '与 AI 大模型进行对话',
  label: 'AI 对话',
  properties: {
    stepName: 'AI 对话',
    config: {
      fields: [
        { label: 'AI 回答内容', value: 'answer' },
        { label: '思考过程', value: 'reasoning_content' },
        { label: '历史聊天记录', value: 'history_message' },
      ],
    },
  },
}

/* 意图识别节点配置数据 */
export const intentNode = {
  type: WorkflowNodeType.IntentNode,
  text: '将用户问题与用户预设的意图分类进行匹配',
  label: '意图识别',
  properties: {
    stepName: '意图识别',
    config: {
      fields: [
        { label: '分类', value: 'category' },
        { label: '理由', value: 'reason' },
      ],
    },
  },
}

export const dataSourceLocalNode = {
  type: WorkflowNodeType.DataSourceLocalNode,
  x: 360,
  y: 2761.3875,
  text: '上传本地文档，输出文档列表（不解析内容，需配合 “文档内容提取” 节点解析）',
  label: '本地文件',
  properties: {
    kind: WorkflowKind.DataSource,
    height: 728.375,
    stepName: '本地文件',
    input_field_list: [],
    config: { fields: [{ label: '文件列表', value: 'file_list' }] },
    showNode: true,
    user_input_config: {},
    user_input_field_list: [],
  },
}

export const dataSourceWebNode = {
  id: WorkflowNodeType.DataSourceWebNode,
  type: WorkflowNodeType.DataSourceWebNode,
  x: 360,
  y: 2761.3875,
  text: '输入根地址自动抓取 Web 数据（单链接对应单文档），输出含内容的文档列表',
  label: 'Web 站点',
  properties: {
    kind: WorkflowKind.DataSource,
    height: 180,
    stepName: 'Web 站点',
    config: { fields: [{ label: '文档列表', value: 'document_list' }] },
  },
}

export const knowledgeWriteNode = {
  type: WorkflowNodeType.KnowledgeWriteNode,
  text: '将输入的分段列表写入当前知识库，并完成向量化处理',
  label: '知识库写入',
  height: 100,
  properties: { stepName: '知识库写入', config: { fields: [] } },
}

/**
 * 知识库检索配置数据
 */
export const searchKnowledgeNode = {
  type: WorkflowNodeType.SearchKnowledge,
  text: '关联知识库，查找与问题相关的分段',
  label: '知识库检索',
  height: 355,
  properties: {
    stepName: '知识库检索',
    config: {
      fields: [
        { label: '检索结果的分段列表', value: 'paragraph_list' },
        { label: '满足直接回答的分段列表', value: 'is_hit_handling_method_list' },
        { label: '检索结果', value: 'data' },
        { label: '满足直接回答的分段内容', value: 'directly_return' },
      ],
    },
  },
}

/**
 * 文档标签检索
 */
export const searchDocumentNode = {
  type: WorkflowNodeType.SearchDocument,
  text: '从设定的检索范围中，根据文档标签检索出满足条件的文档',
  label: '文档标签检索',
  height: 355,
  properties: {
    width: 600,
    stepName: '文档标签检索',
    config: {
      fields: [
        { label: '知识库列表', value: 'knowledge_list' },
        { label: '文档列表', value: 'document_list' },
      ],
    },
  },
}

export const questionNode = {
  type: WorkflowNodeType.Question,
  text: '根据历史聊天记录优化完善当前问题，更利于匹配知识库分段',
  label: '问题优化',
  height: 345,
  properties: { stepName: '问题优化', config: { fields: [{ label: '问题优化结果', value: 'answer' }] } },
}

export const variableSplittingNode = {
  type: WorkflowNodeType.VariableSplittingNode,
  text: '通过配置JSON Path 表达式，对输入的 JSON 格式变量进行解析和拆分',
  label: '变量拆分',
  height: 345,
  properties: { stepName: '变量拆分', config: { fields: [{ label: '结果', value: 'result' }] } },
}

export const parameterExtractionNode = {
  type: WorkflowNodeType.ParameterExtractionNode,
  text: '利用 AI 模型提取结构化参数',
  label: '参数提取',
  height: 345,
  properties: { width: 430, stepName: '参数提取', config: { fields: [{ label: '结果', value: 'result' }] } },
}

export const conditionNode = {
  type: WorkflowNodeType.Condition,
  text: '根据不同条件执行不同的节点',
  label: '判断器',
  height: 175,
  properties: { width: 600, stepName: '判断器', config: { fields: [{ label: '分支名称', value: 'branch_name' }] } },
}




export const rerankerNode = {
  type: WorkflowNodeType.RerankerNode,
  text: '使用重排模型对多个知识库的检索结果进行二次召回',
  label: '多路召回',
  height: 252,
  properties: {
    stepName: '多路召回',
    config: {
      fields: [
        { label: '重排结果列表', value: 'result_list' },
        { label: '重排结果', value: 'result' },
        { label: '满足直接回答的分段列表', value: 'is_hit_handling_method_list' },
      ],
    },
  },
}

export const formNode = {
  type: WorkflowNodeType.FormNode,
  text: '在问答过程中用于收集用户信息，可以根据收集到表单数据执行后续流程',
  label: '表单收集',
  height: 252,
  properties: {
    width: 600,
    stepName: '表单收集',
    node_data: {
      is_result: true,
      form_field_list: [],
      form_content_format: `${'你好，请先填写下面表单内容：'}
{{form}}
${'填写后请点击【提交】按钮进行提交。'}`,
    },
    config: { fields: [{ label: '表单全部内容', value: 'form_data' }] },
  },
}

export const documentExtractNode = {
  type: WorkflowNodeType.DocumentExtractNode,
  text: '解析输入文档，输出结构化文档内容',
  label: '文档内容提取',
  height: 252,
  properties: {
    stepName: '文档内容提取',
    config: {
      fields: [
        { label: '文档内容', value: 'content' },
        { label: '文档列表', value: 'document_list' },
      ],
    },
  },
}

export const documentSplitNode = {
  type: WorkflowNodeType.DocumentSplitNode,
  text: '按分段策略拆分输入文档内容，输出分段文本列表',
  label: '文档分段',
  height: 252,
  properties: { width: 500, stepName: '文档分段', config: { fields: [{ label: '分段列表', value: 'paragraph_list' }] } },
}

export const imageUnderstandNode = {
  type: WorkflowNodeType.ImageUnderstandNode,
  text: '识别出图片中的对象、场景等信息回答用户问题',
  label: '图片理解',
  height: 252,
  properties: { stepName: '图片理解', config: { fields: [{ label: 'AI 回答内容', value: 'answer' }] } },
}

export const videoUnderstandNode = {
  type: WorkflowNodeType.VideoUnderstandNode,
  text: '识别出视频中的对象、场景等信息回答用户问题',
  label: '视频理解',
  height: 252,
  properties: { stepName: '视频理解', config: { fields: [{ label: 'AI 回答内容', value: 'answer' }] } },
}

export const variableAggregationNode = {
  type: WorkflowNodeType.VariableAggregationNode,
  text: '按聚合策略聚合每组的变量',
  label: '变量聚合',
  height: 252,
  properties: { stepName: '变量聚合', config: { fields: [] } },
}

export const variableAssignNode = {
  type: WorkflowNodeType.VariableAssignNode,
  text: '更新全局变量的值',
  label: '变量赋值',
  height: 252,
  properties: { stepName: '变量赋值', config: {} },
}

export const mcpNode = {
  type: WorkflowNodeType.McpNode,
  text: '通过 SSE/Streamable HTTP 方式执行MCP服务中的工具',
  label: 'MCP 调用',
  height: 252,
  properties: { stepName: 'MCP 调用', config: { fields: [{ label: '结果', value: 'result' }] } },
}

export const imageGenerateNode = {
  type: WorkflowNodeType.ImageGenerateNode,
  text: '根据提供的文本内容生成图片',
  label: '图片生成',
  height: 252,
  properties: {
    stepName: '图片生成',
    config: {
      fields: [
        { label: 'AI 回答内容', value: 'answer' },
        { label: '图片', value: 'image' },
      ],
    },
  },
}

export const speechToTextNode = {
  type: WorkflowNodeType.SpeechToTextNode,
  text: '将音频通过语音识别模型转换为文本',
  label: '语音转文本',
  height: 252,
  properties: { stepName: '语音转文本', config: { fields: [{ label: '结果', value: 'result' }] } },
}

export const textToSpeechNode = {
  type: WorkflowNodeType.TextToSpeechNode,
  text: '将文本通过语音合成模型转换为音频',
  label: '文本转语音',
  height: 252,
  properties: { stepName: '文本转语音', config: { fields: [{ label: '结果', value: 'result' }] } },
}

/**
 * 自定义工具配置数据
 */
export const toolNode = {
  type: WorkflowNodeType.ToolLibCustom,
  text: '通过执行自定义脚本，实现数据处理',
  label: '自定义工具',
  height: 260,
  properties: { stepName: '自定义工具', config: { fields: [{ label: '结果', value: 'result' }] } },
}



export const loopStartNode = {
  id: WorkflowNodeType.LoopStartNode,
  type: WorkflowNodeType.LoopStartNode,
  x: 480,
  y: 3340,
  properties: {
    height: 364,
    stepName: '循环开始',
    config: {
      fields: [
        { label: '下标', value: 'index' },
        { label: '循环元素', value: 'item' },
      ],
      globalFields: [],
    },
    showNode: true,
  },
}

export const loopNode = {
  type: WorkflowNodeType.LoopNode,
  visible: false,
  text: '通过设置循环次数和逻辑，重复执行一系列任务',
  label: '循环节点',
  height: 252,
  properties: {
    stepName: '循环节点',
    workflow: {
      edges: [],
      nodes: [
        {
          x: 480,
          y: 3340,
          id: 'loop-start-node',
          type: 'loop-start-node',
          properties: { config: { fields: [], globalFields: [] }, fields: [], height: 361.333, showNode: true, stepName: '开始', globalFields: [] },
        },
      ],
    },
    config: { fields: [] },
  },
}

export const imageToVideoNode = {
  type: WorkflowNodeType.ImageToVideoGenerateNode,
  text: '根据提供的图片生成视频',
  label: '图生视频',
  height: 252,
  properties: { stepName: '图生视频', config: { fields: [{ label: '视频', value: 'video' }] } },
}

export const loopBodyNode = {
  type: WorkflowNodeType.LoopBodyNode,
  text: '循环体',
  label: '循环体',
  height: 1080,
  properties: { width: 1920, stepName: '循环体', config: { fields: [] } },
}

export const loopContinueNode = {
  type: WorkflowNodeType.LoopContinueNode,
  text: '用于终止当前循环，执行下次循环',
  label: 'Continue',
  height: 100,
  properties: { width: 600, stepName: 'Continue', config: { fields: [] } },
}

export const textToVideoNode = {
  type: WorkflowNodeType.TextToVideoGenerateNode,
  text: '根据提供的文本内容生成视频',
  label: '文生视频',
  height: 252,
  properties: { stepName: '文生视频', config: { fields: [{ label: '视频', value: 'video' }] } },
}

export const loopBreakNode = {
  type: WorkflowNodeType.LoopBreakNode,
  text: '终止当前循环，跳出循环体',
  label: 'Break',
  height: 100,
  properties: { width: 600, stepName: 'Break', config: { fields: [] } },
}

/**
 * 工具配置数据
 */
export const toolLibNode = {
  type: WorkflowNodeType.ToolLib,
  text: '通过执行自定义脚本，实现数据处理',
  label: '自定义工具',
  height: 170,
  properties: { stepName: '自定义工具', config: { fields: [{ label: '结果', value: 'result' }] } },
}

/**
 * 工作流工具配置数据
 */
export const toolWorkflowLibNode = {
  type: WorkflowNodeType.ToolWorkflowLib,
  text: '工作流工具',
  label: '工作流工具',
  height: 170,
  properties: { stepName: '工作流工具', config: { fields: [] } },
}

export const applicationNode = {
  type: WorkflowNodeType.Application,
  text: '智能体节点',
  label: '智能体节点',
  height: 260,
  properties: { stepName: '智能体节点', config: { fields: [{ label: '结果', value: 'result' }] } },
}
