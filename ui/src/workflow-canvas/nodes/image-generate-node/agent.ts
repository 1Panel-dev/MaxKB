import { getNode, readNodeData, validatePromptVariables, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { createUpdateTool, getModelsTool, MODEL_FIELD_SCHEMA, modelSlot, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** image-generate-node（图片生成）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const MODEL = modelSlot('TTI', '文生图模型')

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    materials: { type: 'array', items: {}, description: '提示词素材：用户需求、上游输出等，写进提示词' },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    prompt: { type: 'string', description: '正向提示词：要生成什么样的图片，以 {{节点名称.字段}} 写入入参 materials' },
    negative_prompt: { type: 'string', description: '反向提示词：不希望出现的内容，可省略' },
    dialogue_number: { type: 'number', description: '携带的历史对话轮数，默认 0' },
    dialogue_type: { type: 'string', enum: ['NODE', 'WORKFLOW'], description: '历史来源：NODE 本节点问答（默认），WORKFLOW 工作流问答' },
    is_result: { type: 'boolean', description: '是否把结果输出给用户，默认 true' },
  },
  required: ['model', 'prompt'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    answer: { type: 'string', description: '含生成图片的回答内容，可直接输出给用户' },
    image: { type: 'array', description: '生成的图片列表' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'image-generate-node（图片生成）配置要点：',
      '- model：工作流已配置默认文生图模型时传 "default"，否则先 get_models 选真实模型 id。',
      '- prompt 写清要生成的图片的主体、风格与细节，按已绑定入参 materials 的写法引用素材；negative_prompt 可省略。',
      '- is_result：结果直接给用户时为 true。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const modelFields = resolveModelFields(context, args.model, MODEL)
        if (typeof modelFields === 'string') return modelFields
        const error =
          validatePromptVariables(context.lf, context.nodeId, args.prompt, 'prompt') ??
          validatePromptVariables(context.lf, context.nodeId, args.negative_prompt, 'negative_prompt')
        if (error) return error
        const nodeData = readNodeData<Record<string, unknown>>(node)
        writeNodeProperties(node, {
          node_data: {
            ...nodeData,
            ...modelFields,
            prompt: String(args.prompt ?? nodeData.prompt ?? ''),
            negative_prompt: typeof args.negative_prompt === 'string' ? args.negative_prompt : (nodeData.negative_prompt ?? ''),
            dialogue_number: Number(args.dialogue_number ?? nodeData.dialogue_number ?? 0),
            dialogue_type: args.dialogue_type === 'NODE' || args.dialogue_type === 'WORKFLOW' ? args.dialogue_type : (nodeData.dialogue_type ?? 'NODE'),
            is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? true),
          },
        })
        return null
      }),
      getModelsTool(context, MODEL),
    ],
  })
}

export default {
  description: '用文生图模型按提示词生成图片',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
