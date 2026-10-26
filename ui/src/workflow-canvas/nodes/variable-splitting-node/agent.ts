import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** variable-splitting-node（变量拆分）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    input: { type: 'any', description: '要拆分的上游变量（JSON 对象或数组）', 'x-bind': 'input_variable' },
  },
  required: ['input'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    variables: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string', description: '变量名，英文' },
          label: { type: 'string', description: '显示名称' },
          expression: { type: 'string', description: 'JSONPath 表达式，如 $.name、$.items[0].id' },
        },
        required: ['field', 'label', 'expression'],
      },
      description: '要拆出的变量：field 变量名，label 显示名称，expression JSONPath 表达式',
    },
  },
  required: ['variables'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    result: { type: 'object', description: '全部拆分结果（变量名 → 值）' },
  },
  additionalProperties: {
    description: '每个拆分变量一个返回字段：字段名为 config.variables[].field，值为表达式匹配结果',
    'x-from': 'variables',
  },
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'variable-splitting-node（变量拆分）配置要点：',
      '- 要拆分的变量已由入参 input 绑定。',
      '- variables：每项一个拆出的变量，field 英文变量名，label 显示名称，expression 为 JSONPath（如 $.name）。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前变量拆分节点：要拆出的变量与 JSONPath 表达式。要拆分的变量已由入参 input 绑定。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const variables = (Array.isArray(args.variables) ? args.variables : []) as Array<Record<string, string>>
          if (!variables.length) return new ErrorResult('variables 至少一个变量')
          const names = new Set<string>()
          for (const variable of variables) {
            if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(String(variable.field))) return new ErrorResult(`变量名不合法：${variable.field}`)
            if (names.has(variable.field!)) return new ErrorResult(`变量名重复：${variable.field}`)
            if (!String(variable.expression ?? '').trim()) return new ErrorResult(`变量 ${variable.field} 缺少 expression`)
            names.add(variable.field!)
          }
          const variableList = variables.map((variable) => ({
            field: variable.field,
            label: variable.label || variable.field,
            expression: variable.expression,
          }))
          writeNodeProperties(node, {
            node_data: { ...readNodeData<Record<string, unknown>>(node), variable_list: variableList },
            config: {
              ...(node.properties.config as Record<string, unknown>),
              fields: [{ label: '结果', value: 'result' }, ...variableList.map((variable) => ({ label: variable.label, value: variable.field }))],
            },
          })
          node.clearNextNodeField(true)
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description: '按 JSONPath 从一个 JSON 变量中拆出多个字段，供下游分别引用（如从工具返回结果中取出 name、id）',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
