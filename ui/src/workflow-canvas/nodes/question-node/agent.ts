import { getNode, readNodeData, validatePromptVariables, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import {
  argReference,
  finishWithValidate,
  getModelsTool,
  MODEL_FIELD_SCHEMA,
  promptVariableOf,
  resolveModelFields,
  useNodeAgent,
} from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** question-node（问题优化）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    question: { type: 'string', description: '待优化的问题，通常为用户问题' },
  },
  required: ['question'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    system: { type: 'string', description: '系统提示词，可省略（节点自带问题优化角色设定）' },
    prompt: { type: 'string', description: '用户提示词，默认为入参 question 的变量' },
    dialogue_number: { type: 'number', description: '历史对话轮数，默认 1' },
    dialogue_type: { type: 'string', enum: ['NODE', 'WORKFLOW'], description: '历史来源：NODE 本节点问答（默认），WORKFLOW 工作流问答' },
    is_result: { type: 'boolean', description: '是否输出给用户，默认 false' },
  },
  required: ['model'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    answer: { type: 'string', description: '优化后的问题' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  const question = argReference(context, 'question')
  const defaultPrompt = question ? promptVariableOf(context, question) : '{{开始.question}}'
  return useNodeAgent(context, {
    prompt: [
      'question-node（问题优化）配置要点：',
      '- model：已配置默认模型时传 "default"，否则 get_models 选 id。',
      '- system 可省略；需要特殊改写规则时再给。',
      `- prompt：通常就是入参 question 的变量 ${defaultPrompt}，可省略。`,
      '- dialogue_number / dialogue_type：携带的历史对话轮数；历史来源 NODE 为本节点自己的问答（默认），WORKFLOW 为整个工作流的问答。',
      '- 优化结果一般作为中间结果，is_result=false。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前问题优化节点：模型、系统/用户提示词、历史对话、是否输出给用户等。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const modelFields = resolveModelFields(context, args.model)
          if (typeof modelFields === 'string') return new ErrorResult(modelFields)
          const error = validatePromptVariables(context.lf, context.nodeId, args.prompt, 'prompt')
          if (error) return new ErrorResult(error)
          const nodeData = readNodeData<Record<string, unknown>>(node)
          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              ...modelFields,
              ...(typeof args.system === 'string' && args.system ? { system: args.system } : {}),
              prompt: typeof args.prompt === 'string' && args.prompt ? args.prompt : defaultPrompt,
              dialogue_number: Number(args.dialogue_number ?? nodeData.dialogue_number ?? 1),
              dialogue_type: args.dialogue_type === 'NODE' || args.dialogue_type === 'WORKFLOW' ? args.dialogue_type : (nodeData.dialogue_type ?? 'NODE'),
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? false),
            },
          })
          return finishWithValidate(context)
        },
      },
      getModelsTool(context),
    ],
  })
}

export default {
  description: '结合历史对话把用户问题改写得更完整清晰；通常接在知识库检索之前，检索问题改为引用它的 answer',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
