import type { LlmTool } from './types'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import {
  getDefaultModelConfig,
  getNode,
  readNodeData,
  validatePromptVariables,
  writeNodeProperties,
} from '@/workflow-canvas/ai-generate/tools/canvas'
import {
  LLM_MODEL,
  MODEL_FIELD_SCHEMA,
  argReference,
  argReferences,
  finishWithValidate,
  getModelsTool,
  promptVariableOf,
  useNodeAgent,
} from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import { normalizeTool } from './types'

/** llm-node（大语言模型）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    materials: {
      type: 'array',
      items: {},
      description: '传给模型的上下文素材：用户问题、检索结果、上游输出等',
      'x-bind': 'context_variable',
    },
    model_reference: {
      type: 'array',
      description: '引用上游变量作为模型（model_type=reference 时绑定）',
      'x-bind': 'model_id_reference',
    },
    tools_reference: {
      type: 'array',
      description: '引用上游输出的工具定义作为「工具声明」（tools_location=reference 时绑定）；一般不传，由配置 agent 在 requirement 里声明工具',
    },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model_type: {
      type: 'string',
      enum: ['default', 'custom', 'reference'],
      description: '模型来源：default 用工作流默认模型，custom 用下方 model 选具体模型，reference 引用上游变量',
    },
    model: MODEL_FIELD_SCHEMA,
    model_params_setting: { type: 'object', description: '模型参数（temperature 等），按所选模型的可用参数设置，不传则保持默认' },
    system: { type: 'string', description: '系统提示词（角色设定），写清身份、目标、回答规范与限制' },
    prompt: { type: 'string', description: '用户提示词，以 {{节点名称.字段}} 引用入参 materials' },
    enable_context: { type: 'boolean', description: '是否携带已绑定入参 materials 作为上下文，绑定后默认开启' },
    tools_location: { type: 'string', enum: ['customize', 'reference'], description: '工具声明来源：customize 用下方 tools 声明函数，reference 引用入参 tools_reference 的上游工具定义' },
    tools: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          name: { type: 'string' },
          description: { type: 'string', description: '工具作用说明，模型据此决定是否调用' },
          parameters: { type: 'object', description: '函数参数 JSON Schema（properties + required），说明参数与类型' },
        },
        required: ['name'],
      },
      description: '模型可调用的工具声明（Function Calling），调用请求经 tool_calls 返回、不在本节点执行。传空数组表示清空',
    },
    is_result: { type: 'boolean', description: '是否把回答输出给用户：最终回答为 true，中间加工为 false' },
  },
  required: ['model_type'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    content: { type: 'string', description: '回答内容' },
    reasoning_content: { type: 'string', description: '思考内容' },
    refusal: { type: 'string', description: '拒答内容（拒答时返回）' },
    is_refusal: { type: 'boolean', description: '是否拒答' },
    tool_calls: { type: 'array', description: '模型决定调用的工具名与参数列表' },
    finish_reason: { type: 'string', description: '结束原因' },
  },
  additionalProperties: false,
}

/** 把模型给的函数声明归一化为节点工具列表；非法项返回错误文本 */
function normalizeTools(value: unknown): LlmTool[] | string {
  if (!Array.isArray(value)) return 'tools 应为数组'
  const tools: LlmTool[] = []
  for (const [index, item] of value.entries()) {
    const tool = normalizeTool(item)
    if (tool === null) return `tools[${index}] 缺少函数名 name`
    tools.push(tool)
  }
  return tools
}

function useAgent(context: NodeAgentContext) {
  const { source, id, reference } = LLM_MODEL.fields
  const materialRefs = argReferences(context, 'materials')
  const defaultPrompt = materialRefs.length ? materialRefs.map((ref) => promptVariableOf(context, ref)).join('\n') : '{{开始.question}}'
  return useNodeAgent(context, {
    prompt: [
      'llm-node（大语言模型）配置要点：',
      '- model_type：default 用工作流默认模型（已配置时首选）；custom 用 get_models 选模型 id；reference 引用上游模型变量（需绑定入参 model_reference）。',
      '- system：角色设定，写清身份、目标、回答规范与限制（按需求生成完整内容，不要留占位）。',
      '- prompt：用户提示词，按已绑定入参 materials 给出的 {{节点名称.字段}} 写法引用上下文素材。',
      '- enable_context：携已绑定入参 materials 作上下文，绑定时默认开启，无需配置。',
      '- 工具声明：需求要求模型可调用工具（Function Calling）时，在 tools 里以 {name,description,parameters} 声明函数（parameters 为 JSON Schema，写清字段与类型）；调用请求经 tool_calls 返回、不在本节点执行。工具声明通过本 update 工具写入，属于节点配置，不需要父节点的入参。',
      '- tools_location：默认 customize（在 tools 里直接声明）；仅当父节点已绑定入参 tools_reference 提供工具定义时才用 reference。',
      '- model_params_setting：按所选模型设置 temperature 等参数，未提及时保持默认。',
      '- is_result：作为流程最终回答时为 true，作为中间加工步骤时为 false。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前大语言模型节点：模型来源与模型参数、系统/用户提示词、是否携带上下文、工具声明、是否输出给用户。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)

          const modelType = args.model_type === 'custom' ? 'custom' : args.model_type === 'reference' ? 'reference' : 'default'
          let modelFields: Record<string, unknown>
          let defaultMissing = false
          if (modelType === 'reference') {
            const modelRef = argReference(context, 'model_reference')
            if (!modelRef) return new ErrorResult('model_type=reference 需要父节点传入入参 model_reference，请先把模型引用绑定到上游变量')
            modelFields = { [source]: 'reference', [id]: '', [reference]: [...modelRef] }
          } else if (modelType === 'custom') {
            if (!args.model) return new ErrorResult('model_type=custom 需要传 model，请先 get_models 选择模型 id')
            modelFields = { [source]: 'custom', [id]: String(args.model), [reference]: [] }
          } else {
            modelFields = { [source]: 'default', [id]: '', [reference]: [] }
            defaultMissing = !getDefaultModelConfig(context.lf, LLM_MODEL.type)?.model_id
          }

          const promptError = validatePromptVariables(context.lf, context.nodeId, args.prompt, 'prompt')
          if (promptError) return new ErrorResult(promptError)

          const nodeData = readNodeData<Record<string, unknown>>(node)
          const toolsFields: Record<string, unknown> = {}
          const toolsRefs = argReferences(context, 'tools_reference')
          const toolsLocation =
            args.tools_location === 'reference' ? 'reference' : args.tools_location === 'customize' ? 'customize' : toolsRefs.length ? 'reference' : undefined
          if (toolsLocation === 'reference') {
            if (!toolsRefs.length) {
              return new ErrorResult('tools_location=reference 需要父节点传入入参 tools_reference，请改用 customize 直接声明工具，或先绑定上游工具变量')
            }
            toolsFields.tools = { location: 'reference', reference: toolsRefs.map((ref) => [...ref]), tools: [] }
          } else if (args.tools !== undefined) {
            const tools = normalizeTools(args.tools)
            if (typeof tools === 'string') return new ErrorResult(tools)
            toolsFields.tools = { location: 'customize', reference: [], tools }
          }

          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              ...modelFields,
              ...toolsFields,
              system: typeof args.system === 'string' && args.system ? args.system : (nodeData.system ?? ''),
              prompt: typeof args.prompt === 'string' && args.prompt ? args.prompt : defaultPrompt,
              enable_context: typeof args.enable_context === 'boolean' ? args.enable_context : (materialRefs.length ? true : (nodeData.enable_context ?? false)),
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? true),
              ...(args.model_params_setting !== undefined ? { model_params_setting: args.model_params_setting } : {}),
            },
          })
          if (defaultMissing) {
            return new ErrorResult(
              `当前工作流未配置默认${LLM_MODEL.label}（需要在默认模型设置中配置 LLM），所以节点无法使用默认模型。请改用 model_type=custom 选取具体模型，或提醒用户先配置默认 LLM 模型后重试`,
            )
          }
          return finishWithValidate(context)
        },
      },
      getModelsTool(context, LLM_MODEL),
    ],
  })
}

export default {
  description:
    '单次调用大模型生成回答，可声明工具（Function Calling）由模型决定调用，工具调用经 tool_calls 返回、不在本节点执行；' +
    '面向用户的最终回答 is_result=true，中间加工步骤为 false；基于知识库时提示词引用检索结果与用户问题',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
