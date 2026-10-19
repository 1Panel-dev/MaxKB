import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { createUpdateTool, getModelsTool, MODEL_FIELD_SCHEMA, modelSlot, resolveModelFields, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** reranker-node（多路召回）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const MODEL = modelSlot('RERANKER', '重排模型', 'reranker_model')

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    contents: { type: 'array', items: {}, description: '要重排的多路检索结果，常为多个知识库检索的 paragraph_list', 'x-bind': 'reranker_reference_list' },
    question: { type: 'string', description: '检索问题，通常为用户问题', 'x-bind': 'question_reference_address' },
  },
  required: ['contents', 'question'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model: MODEL_FIELD_SCHEMA,
    top_n: { type: 'number', description: '保留的分段数，默认 3' },
    similarity: { type: 'number', description: '分数阈值，默认 0' },
    max_paragraph_char_number: { type: 'number', description: '引用分段最大字符数，默认 5000' },
    show_knowledge: { type: 'boolean', description: '是否把结果展示给用户，默认 false' },
  },
  required: ['model'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    result_list: { type: 'array', description: '重排后的分段列表' },
    result: { type: 'string', description: '重排后拼接好的分段文本，适合放进提示词' },
    is_hit_handling_method_list: { type: 'array', description: '满足直接回答的分段列表' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'reranker-node（多路召回）配置要点：',
      '- model：工作流已配置默认重排模型时传 "default"，否则先 get_models 选真实模型 id。',
      '- 重排内容与检索问题已由入参 contents / question 绑定，无需配置。',
      '- top_n、similarity、max_paragraph_char_number 按需求设置，未提及时保持默认。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const modelFields = resolveModelFields(context, args.model, MODEL)
        if (typeof modelFields === 'string') return modelFields
        const nodeData = readNodeData<Record<string, unknown> & { reranker_setting?: Record<string, unknown> }>(node)
        writeNodeProperties(node, {
          node_data: {
            ...nodeData,
            ...modelFields,
            show_knowledge: typeof args.show_knowledge === 'boolean' ? args.show_knowledge : (nodeData.show_knowledge ?? false),
            reranker_setting: {
              top_n: 3,
              similarity: 0,
              max_paragraph_char_number: 5000,
              ...nodeData.reranker_setting,
              ...(args.top_n !== undefined ? { top_n: Number(args.top_n) } : {}),
              ...(args.similarity !== undefined ? { similarity: Number(args.similarity) } : {}),
              ...(args.max_paragraph_char_number !== undefined ? { max_paragraph_char_number: Number(args.max_paragraph_char_number) } : {}),
            },
          },
        })
        return null
      }),
      getModelsTool(context, MODEL),
    ],
  })
}

export default {
  description: '用重排模型对多路检索结果（如多个知识库检索）二次排序召回，提升相关性；结果 result 可放进 AI 对话提示词',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
