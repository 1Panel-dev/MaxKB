import { getNode, readNodeData, validatePromptVariables, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { finishWithValidate, getModelsTool, MODEL_FIELD_SCHEMA, modelSlot, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** image-to-video-node（图生视频）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const MODEL = modelSlot('ITV', '图生视频模型')

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    materials: { type: 'array', items: {}, description: '提示词素材：用户需求、上游输出等，写进提示词' },
    first_frame: { type: 'array', description: '首帧图片', 'x-bind': 'first_frame_url' },
    last_frame: { type: 'array', description: '尾帧图片（可选）', 'x-bind': 'last_frame_url' },
  },
  required: ['first_frame'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    prompt: { type: 'string', description: '正向提示词：要生成什么样的视频，以 {{节点名称.字段}} 写入入参 materials' },
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
    video: { type: 'array', description: '生成的视频列表' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'image-to-video-node（图生视频）配置要点：',
      '- model：工作流已配置默认图生视频模型时传 "default"，否则先 get_models 选真实模型 id。',
      '- prompt 写清要生成的视频的主体、风格与细节，按已绑定入参 materials 的写法引用素材；negative_prompt 可省略。',
      '- 首帧 / 尾帧图片已由入参 first_frame / last_frame 绑定，无需配置。',
      '- is_result：结果直接给用户时为 true。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前图生视频节点：模型、正向/反向提示词、是否输出给用户等。首帧/尾帧图片已由入参绑定。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const modelFields = resolveModelFields(context, args.model, MODEL)
          if (typeof modelFields === 'string') return new ErrorResult(modelFields)
          const error =
            validatePromptVariables(context.lf, context.nodeId, args.prompt, 'prompt') ??
            validatePromptVariables(context.lf, context.nodeId, args.negative_prompt, 'negative_prompt')
          if (error) return new ErrorResult(error)
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
          return finishWithValidate(context)
        },
      },
      getModelsTool(context, MODEL),
    ],
  })
}

export default {
  description: '用图生视频模型以首帧（可选尾帧）图片为基础按提示词生成视频；图片常来自开始节点用户上传的 image',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
