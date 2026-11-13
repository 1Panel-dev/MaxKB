import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/**
 * tool-workflow-lib-node（工作流工具）的 AI 生成配置：为工具自己工作流声明的每个输入参数赋值。
 * 与 tool-lib-node 是同一类节点（都是「工具」），但签名来自绑定的工作流工具自身的基本信息节点，
 * 新增节点（add_node）时已按真实签名写入 node_data.input_field_list，这里只负责逐个赋值。
 */

interface WorkflowToolInputField {
  field: string
  source: 'reference' | 'custom'
  type?: string
  is_required?: boolean
  desc?: string
  value: unknown
}

const params: JsonObjectSchema = {
  type: 'object',
  properties: {},
  additionalProperties: {
    type: 'any',
    description: '要用引用绑定的输入参数，键为参数名（get_tools / add_node 返回的 inputs 的 name）。工作流工具的每个参数都可以是引用或常量，具体哪些用引用由这里决定，不是固定的',
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    values: { type: 'object', description: '工作流工具中 source=custom 的输入参数：参数名 → 常量值' },
    is_result: { type: 'boolean', description: '是否把工作流工具的输出结果输出给用户，默认 false' },
  },
}

const returns: JsonObjectSchema = { type: 'object', properties: {}, additionalProperties: true }

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'tool-workflow-lib-node（工作流工具）配置要点：为工作流工具的每个输入参数赋值。与自定义工具不同，这里每个参数都可以是引用或常量，不是工具本身固定的。',
      '- 要引用上游数据的参数，在父 agent 调 configure_node 时按参数名传入同名引用（本节点形参即该参数名），这里无需再配置；要给常量的参数在 values 里给值。',
      '- 必填参数都要有值（引用或常量二选一）；is_result 表示是否把工作流工具的输出结果输出给用户（默认 false）。',
      '- 工作流工具的输出字段是它自己声明的输出参数（动态，见本节点的返回字段要求），不是固定的 result。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前工作流工具节点：为工具的每个输入参数赋值、是否输出给用户。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const nodeData = readNodeData<Record<string, unknown> & { input_field_list?: WorkflowToolInputField[] }>(node)
          const values = (args.values ?? {}) as Record<string, unknown>
          const inputFields: WorkflowToolInputField[] = []
          for (const field of nodeData.input_field_list ?? []) {
            // 每个参数都可能是引用或常量：本次传了同名引用就用引用（不管之前是什么来源）；
            // 没传引用时，之前已是引用的保持不变（续聊未重新绑定），否则按 values 给常量
            const reference = argReference(context, field.field)
            if (reference) {
              inputFields.push({ ...field, source: 'reference', value: [...reference] })
              continue
            }
            if (field.source === 'reference') {
              inputFields.push(field)
              continue
            }
            const value = values[field.field]
            if (value === undefined) {
              if (field.is_required) return new ErrorResult(`必填参数 ${field.field} 未赋值：引用上游数据传 args.${field.field}，给常量传 values.${field.field}`)
              inputFields.push(field)
              continue
            }
            inputFields.push({ ...field, source: 'custom', value })
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
  description: '调用已发布的工作流工具，相当于调用一个子工作流（新增时需 tool_id，用 get_tools 查询）；入参为该工具自己声明的输入参数，输出为它声明的输出参数',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
