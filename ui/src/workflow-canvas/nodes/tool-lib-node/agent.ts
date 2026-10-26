import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

interface ToolNodeInputField {
  name: string
  source: 'reference' | 'custom'
  type?: string
  is_required?: boolean
  desc?: string
  value: unknown
}

/** tool-lib-node（工具）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {},
  additionalProperties: { type: 'any', description: '工具中 source=reference 的输入参数，键为参数名（get_tools 返回的 inputs）' },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    values: { type: 'object', description: '工具中 source=custom 的输入参数：参数名 → 常量值' },
    is_result: { type: 'boolean', description: '是否把工具结果输出给用户，默认 false' },
  },
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    result: { type: 'any', description: '工具返回值' },
  },
  additionalProperties: false,
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'tool-lib-node（工具）配置要点：为工具的每个输入参数赋值。',
      '- source 为 reference 的参数由同名入参绑定，无需配置；source 为 custom 的参数在 values 里给常量值。',
      '- 必填参数都要有值；is_result 表示是否把工具结果输出给用户（默认 false）。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前工具节点：为工具的每个输入参数赋值、是否输出给用户。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const nodeData = readNodeData<Record<string, unknown> & { input_field_list?: ToolNodeInputField[] }>(node)
          const values = (args.values ?? {}) as Record<string, unknown>
          const inputFields: ToolNodeInputField[] = []
          for (const field of nodeData.input_field_list ?? []) {
            if (field.source === 'reference') {
              const reference = argReference(context, field.name)
              if (!reference && field.is_required) return new ErrorResult(`必填参数 ${field.name} 需要父节点传入同名入参`)
              inputFields.push(reference ? { ...field, value: [...reference] } : field)
              continue
            }
            const value = values[field.name]
            if (value === undefined) {
              if (field.is_required) return new ErrorResult(`必填参数 ${field.name} 未赋值`)
              inputFields.push(field)
              continue
            }
            inputFields.push({ ...field, value: typeof value === 'string' ? value : JSON.stringify(value) })
          }
          writeNodeProperties(node, {
            node_data: {
              ...nodeData,
              input_field_list: inputFields,
              is_result: typeof args.is_result === 'boolean' ? args.is_result : (nodeData.is_result ?? false),
            },
          })
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description: '调用工具库中的自定义工具，相当于调用一个外部函数（新增时需 tool_id，用 get_tools 查询）；入参为工具中 source=reference 的参数',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
