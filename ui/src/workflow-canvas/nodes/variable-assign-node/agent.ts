import { randomId } from '@/utils/common'
import { getFieldOptions, getNode, readNodeData, validateReference, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { createUpdateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

const VALUE_TYPES = ['string', 'num', 'json', 'bool']

/** variable-assign-node（变量赋值）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    values: { type: 'array', items: {}, description: '要赋给变量的上游数据（source=referencing 时引用）' },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    variables: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          target: { type: 'array', items: { type: 'string' } },
          source: { type: 'string', enum: ['custom', 'referencing'] },
          type: { type: 'string', enum: VALUE_TYPES },
          value: { description: 'source=custom 时的值' },
          reference: { type: 'array', items: { type: 'string' } },
        },
        required: ['target', 'source'],
      },
      description: '赋值列表：target 目标变量，source 常量 / 引用，type 值类型，value 常量值，reference 引用（取自入参 values）',
    },
  },
  required: ['variables'],
}

const returns: JsonObjectSchema = { type: 'object', properties: {}, additionalProperties: false }

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'variable-assign-node（变量赋值）配置要点：',
      '- target：要赋值的变量 [分组, 变量名]，分组为 global / chat / loop，必须是 get_field_options 里已存在的变量（无法新建变量）。',
      '- source="custom"：value 为常量（type 为 string 时可含 {{节点名称.字段}} 变量）；source="referencing"：reference 使用已绑定入参 values 中的引用。',
      '- type：string / num / json / bool。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const variables = Array.isArray(args.variables) ? (args.variables as Array<Record<string, unknown>>) : []
        if (!variables.length) return 'variables 至少一项'
        const groups = getFieldOptions(context.lf, context.nodeId)
        const variableList = []
        for (const [index, variable] of variables.entries()) {
          const target = Array.isArray(variable.target) ? variable.target.map(String) : []
          if (!['global', 'chat', 'loop', 'output'].includes(target[0] ?? '')) return `variables[${index}].target 只能是 global/chat/loop 变量`
          const error = validateReference(context.lf, context.nodeId, target, `variables[${index}].target`)
          if (error) return error
          const referencing = variable.source === 'referencing'
          if (referencing) {
            const referenceError = validateReference(context.lf, context.nodeId, variable.reference, `variables[${index}].reference`)
            if (referenceError) return referenceError
          }
          const type = VALUE_TYPES.includes(String(variable.type)) ? String(variable.type) : 'string'
          variableList.push({
            id: randomId(),
            fields: target,
            name: groups.find((group) => group.nodeId === target[0])?.fields.find((field) => field.value === target[1])?.label ?? target[1],
            source: referencing ? 'referencing' : 'custom',
            type,
            value: referencing
              ? null
              : type === 'json' && typeof variable.value !== 'string'
                ? JSON.stringify(variable.value)
                : (variable.value ?? ''),
            reference: referencing ? (variable.reference as unknown[]).map(String) : [],
          })
        }
        writeNodeProperties(node, { node_data: { ...readNodeData<Record<string, unknown>>(node), variable_list: variableList } })
        return null
      }),
    ],
  })
}

export default {
  description: '相当于赋值语句：给全局变量 / 会话变量 / 循环变量赋值，不产生输出',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
