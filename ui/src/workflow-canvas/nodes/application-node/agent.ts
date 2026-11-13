import { getNode, readNodeData, validateReference, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/**
 * application-node（智能体节点）的 AI 生成配置：把用户问题与智能体需要的参数都绑定成引用。
 * 与工具节点不同，这里的入参只能引用上游数据，不支持常量（节点表单本身只有引用选择器，没有常量输入）。
 * 新增节点（add_node）时已按绑定的智能体的开始节点写入 node_data 的 api_input_field_list / user_input_field_list。
 */

interface ApiInputField {
  variable: unknown
  is_required: boolean
  value: string[]
}

interface UserInputField {
  field: string
  required: boolean
  value: string[]
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    question: { type: 'array', items: { type: 'string' }, description: '交给智能体的用户问题（引用上游的一个字段）' },
  },
  required: ['question'],
  additionalProperties: { type: 'array', items: { type: 'string' }, description: '智能体需要的其余参数（api / 表单入参），键为参数名（add_node 返回的 inputs 的 name）' },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    is_result: { type: 'boolean', description: '是否把智能体的回复输出给用户，默认 false（无下游节点时自动为 true）' },
  },
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: { result: { type: 'any', description: '智能体的回复内容' } },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'application-node（智能体节点）配置要点：把用户问题与智能体需要的每个参数都绑定成引用。',
      '- 入参只能引用上游数据，不支持常量；question 必填，是给智能体的用户问题（常见引用开始节点的用户问题，或上游某个字段）。',
      '- 其余入参按 add_node 返回的 inputs 逐个绑定，必填的都要有引用。',
      '- is_result 表示是否把智能体的回复输出给用户（默认 false，没有下游节点时自动为 true）。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前智能体节点：绑定用户问题与智能体需要的每个参数、是否输出给用户。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const nodeData = readNodeData<{ api_input_field_list?: ApiInputField[]; user_input_field_list?: UserInputField[]; question_reference_address?: string[] }>(node)
          const question = argReference(context, 'question')
          if (question) {
            const error = validateReference(context.lf, context.nodeId, question, 'question')
            if (error) return new ErrorResult(error)
          }
          const apiInputFieldList = (nodeData.api_input_field_list ?? []).map((field) => {
            const reference = argReference(context, String(field.variable))
            if (!reference && field.is_required) return new ErrorResult(`必填参数 ${String(field.variable)} 需要父节点传入同名入参`)
            return reference ? { ...field, value: [...reference] } : field
          })
          const apiError = apiInputFieldList.find((item): item is ErrorResult => item instanceof ErrorResult)
          if (apiError) return apiError
          const userInputFieldList = (nodeData.user_input_field_list ?? []).map((field) => {
            const reference = argReference(context, field.field)
            if (!reference && field.required) return new ErrorResult(`必填参数 ${field.field} 需要父节点传入同名入参`)
            return reference ? { ...field, value: [...reference] } : field
          })
          const userError = userInputFieldList.find((item): item is ErrorResult => item instanceof ErrorResult)
          if (userError) return userError
          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              ...(question ? { question_reference_address: [...question] } : {}),
              api_input_field_list: apiInputFieldList as ApiInputField[],
              user_input_field_list: userInputFieldList as UserInputField[],
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData as { is_result?: boolean }).is_result ?? false,
            },
          })
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description: '调用已发布的智能体，相当于把当前对话的一部分交给另一个智能体处理（新增时需 application_id，用 get_applications 查询）；入参只能引用上游数据，输出固定为 result',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
