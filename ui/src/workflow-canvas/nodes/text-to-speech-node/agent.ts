import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { finishWithValidate, getModelsTool, MODEL_FIELD_SCHEMA, modelSlot, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** text-to-speech-node（文本转语音）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const MODEL = modelSlot('TTS', '语音合成模型', 'tts_model')

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    text: { type: 'string', description: '要朗读的文本', 'x-bind': 'content_list' },
  },
  required: ['text'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    is_result: { type: 'boolean', description: '是否把结果输出给用户，默认 true' },
  },
  required: ['model'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    result: { type: 'array', description: '合成的音频列表' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'text-to-speech-node（文本转语音）配置要点：',
      '- model：工作流已配置默认语音合成模型时传 "default"，否则先 get_models 选真实模型 id。',
      '- 要朗读的文本已由入参 text 绑定，无需配置。',
      '- is_result：结果直接给用户时为 true，作为中间步骤时为 false。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前文本转语音节点：模型与是否输出给用户。要朗读的文本已由入参 text 绑定。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const modelFields = resolveModelFields(context, args.model, MODEL)
          if (typeof modelFields === 'string') return new ErrorResult(modelFields)
          const nodeData = readNodeData<Record<string, unknown>>(node)
          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              ...modelFields,
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
  description: '用语音合成模型把文本转成语音，常接在 AI 对话之后朗读回答',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
