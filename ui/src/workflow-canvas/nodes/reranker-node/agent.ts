import { getNode, getDefaultModelConfig, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, getModelsTool, MODEL_FIELD_SCHEMA, modelSlot, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** reranker-node（多路召回）的 AI 生成配置；node_data 协议以节点视图 index.vue 的 defaultForm 为准 */

const MODEL = modelSlot('RERANKER', '重排模型', 'reranker_model')

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    contents: { type: 'array', items: {}, description: '要重排的多路检索结果，常为多个知识库检索的 paragraph_list', 'x-bind': 'reranker_reference_list' },
    question: { type: 'string', description: '检索问题，通常为用户问题', 'x-bind': 'question_reference_address' },
    model_reference: {
      type: 'array',
      description: '引用上游变量作为重排模型（model_type=reference 时绑定）',
      'x-bind': 'reranker_model_id_reference',
    },
  },
  required: ['contents', 'question'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    model_type: {
      type: 'string',
      enum: ['default', 'custom', 'reference'],
      description: '重排模型来源：default 用工作流默认重排模型，custom 用下方 model 选具体模型，reference 引用上游变量',
    },
    model: MODEL_FIELD_SCHEMA,
    top_n: { type: 'number', description: '保留的分段数，默认 3' },
    similarity: { type: 'number', description: '分数阈值，默认 0' },
    max_paragraph_char_number: { type: 'number', description: '引用分段最大字符数，默认 5000' },
    show_knowledge: { type: 'boolean', description: '是否把结果展示给用户，默认 false' },
  },
  required: ['model_type'],
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
  const { source, id, reference } = MODEL.fields
  return useNodeAgent(context, {
    prompt: [
      'reranker-node（多路召回）配置要点：',
      '- model_type：default 用工作流默认重排模型（已配置时首选）；custom 用 get_models 选取的模型 id；reference 引用上游模型变量（需绑定入参 model_reference）。',
      '- 重排内容与检索问题已由入参 contents / question 绑定，无需配置。',
      '- top_n、similarity、max_paragraph_char_number 按需求设置，未提及时保持默认。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前多路召回（重排）节点：模型来源与召回参数。重排内容与问题已由入参绑定。只传要设置的字段，其余保持不变。' +
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
            if (!modelRef) return new ErrorResult('model_type=reference 需要父节点传入入参 model_reference，请先把重排模型引用绑定到上游变量')
            modelFields = { [source]: 'reference', [id]: '', [reference]: [...modelRef] }
          } else if (modelType === 'custom') {
            if (!args.model) return new ErrorResult('model_type=custom 需要传 model，请先 get_models 选择模型 id')
            modelFields = { [source]: 'custom', [id]: String(args.model), [reference]: [] }
          } else {
            modelFields = { [source]: 'default', [id]: '', [reference]: [] }
            defaultMissing = !getDefaultModelConfig(context.lf, MODEL.type)?.model_id
          }

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
          if (defaultMissing) {
            return new ErrorResult(
              `当前工作流未配置默认${MODEL.label}（需要在默认模型设置中配置 RERANKER），所以节点无法使用默认模型。请改用 model_type=custom 选取具体模型，或提醒用户先配置默认重排模型后重试`,
            )
          }
          return finishWithValidate(context)
        },
      },
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
