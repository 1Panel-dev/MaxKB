import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { createUpdateTool, getModelsTool, MODEL_FIELD_SCHEMA, modelSlot, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** speech-to-text-node（语音转文本）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const MODEL = modelSlot('STT', '语音识别模型', 'stt_model')

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    audio: { type: 'array', description: '要识别的音频', 'x-bind': 'audio_list' },
  },
  required: ['audio'],
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
    result: { type: 'string', description: '识别出的文本' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'speech-to-text-node（语音转文本）配置要点：',
      '- model：工作流已配置默认语音识别模型时传 "default"，否则先 get_models 选真实模型 id。',
      '- 要识别的音频已由入参 audio 绑定，无需配置。',
      '- is_result：结果直接给用户时为 true，作为中间步骤时为 false。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const modelFields = resolveModelFields(context, args.model, MODEL)
        if (typeof modelFields === 'string') return modelFields
        const nodeData = readNodeData<Record<string, unknown>>(node)
        writeNodeProperties(node, {
          node_data: {
            ...nodeData,
            ...modelFields,
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
  description: '用语音识别模型把音频转成文本，结果可交给 AI 对话等节点继续处理；音频常来自开始节点用户上传的 audio',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
