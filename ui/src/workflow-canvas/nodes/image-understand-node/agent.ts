import { getNode, readNodeData, validatePromptVariables, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { finishWithValidate, getModelsTool, MODEL_FIELD_SCHEMA, modelSlot, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** image-understand-node（图片理解）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const MODEL = modelSlot('IMAGE', '视觉模型')

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    materials: { type: 'array', items: {}, description: '提示词素材：用户问题、上游输出等，写进提示词' },
    images: { type: 'array', description: '要识别的图片', 'x-bind': 'image_list' },
  },
  required: ['images'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    system: { type: 'string', description: '系统提示词（角色设定），可省略' },
    prompt: { type: 'string', description: '用户提示词：要从图片中看出什么，以 {{节点名称.字段}} 写入入参 materials' },
    dialogue_number: { type: 'number', description: '携带的历史对话轮数，默认 0' },
    dialogue_type: { type: 'string', enum: ['NODE', 'WORKFLOW'], description: '历史来源：NODE 本节点问答（默认），WORKFLOW 工作流问答' },
    is_result: { type: 'boolean', description: '是否把回答输出给用户，默认 true' },
    reasoning_content_enable: { type: 'boolean', description: '是否输出思考过程（仅思考模型需要）' },
  },
  required: ['model', 'prompt'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    answer: { type: 'string', description: '图片理解的回答内容' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'image-understand-node（图片理解）配置要点：',
      '- model：工作流已配置默认视觉模型时传 "default"，否则先 get_models 选真实模型 id。',
      '- 图片已由入参 images 绑定；prompt 写清要从图片中识别什么，按已绑定入参 materials 的写法引用素材。',
      '- is_result：作为最终回答时为 true，作为中间加工步骤时为 false。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前图片理解节点：模型、系统/用户提示词、是否输出给用户、是否输出思考过程等。图片已由入参 images 绑定。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const modelFields = resolveModelFields(context, args.model, MODEL)
          if (typeof modelFields === 'string') return new ErrorResult(modelFields)
          const error =
            validatePromptVariables(context.lf, context.nodeId, args.prompt, 'prompt') ??
            validatePromptVariables(context.lf, context.nodeId, args.system, 'system')
          if (error) return new ErrorResult(error)
          const nodeData = readNodeData<Record<string, unknown> & { model_setting?: Record<string, unknown> }>(node)
          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              ...modelFields,
              system: typeof args.system === 'string' ? args.system : (nodeData.system ?? ''),
              prompt: String(args.prompt ?? nodeData.prompt ?? ''),
              dialogue_number: Number(args.dialogue_number ?? nodeData.dialogue_number ?? 0),
              dialogue_type: args.dialogue_type === 'NODE' || args.dialogue_type === 'WORKFLOW' ? args.dialogue_type : (nodeData.dialogue_type ?? 'NODE'),
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? true),
              model_setting: {
                reasoning_content_start: '<think>',
                reasoning_content_end: '</think>',
                ...nodeData.model_setting,
                reasoning_content_enable:
                  typeof args.reasoning_content_enable === 'boolean'
                    ? args.reasoning_content_enable
                    : !!nodeData.model_setting?.reasoning_content_enable,
              },
            },
          })
          return finishWithValidate(context)
        },
      },
      getModelsTool(context, MODEL),
    ],
  })
}

export default {
  description: '用视觉模型理解图片并按提示词回答（看图问答、图片描述、OCR 等）；图片常来自开始节点用户上传的 image',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
