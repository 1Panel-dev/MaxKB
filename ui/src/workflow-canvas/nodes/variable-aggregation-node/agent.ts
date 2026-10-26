import { randomId } from '@/utils/common'
import { getNode, readNodeData, validateReference, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** variable-aggregation-node（变量聚合）的 AI 生成配置 */

const STRATEGIES = ['first_non_null', 'variable_to_array', 'variable_to_dict']

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    variables: { type: 'array', items: {}, description: '要聚合的上游变量，常为不同分支各自的输出' },
  },
  required: ['variables'],
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    strategy: {
      type: 'string',
      enum: STRATEGIES,
      description: '聚合方式：first_non_null 每组取第一个非空值（默认，常用于汇合分支输出），variable_to_array 每组聚成数组，variable_to_dict 每组聚成字典',
    },
    groups: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string', description: '组变量名，英文' },
          label: { type: 'string', description: '显示名称' },
          variables: {
            type: 'array',
            items: { type: 'array', items: { type: 'string' } },
            description: '组内变量，取自入参 variables 的引用 [节点ID, 字段]',
          },
          keys: { type: 'array', items: { type: 'string' }, description: 'variable_to_dict 时与 variables 一一对应的键名' },
        },
        required: ['field', 'label', 'variables'],
      },
      description: '聚合分组：每组一个输出变量',
    },
  },
  required: ['strategy', 'groups'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {},
  additionalProperties: {
    description: '每个分组一个返回字段：字段名为 config.groups[].field，类型按聚合方式（取首个非空值为该值类型，数组为 array，字典为 object）',
    'x-from': 'groups',
  },
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'variable-aggregation-node（变量聚合）配置要点：',
      '- 汇合多个分支的输出时用 first_non_null：一个分组里放各分支同类的输出，运行时取实际执行分支的那个值。',
      '- 组内 variables 使用已绑定入参 variables 中的引用；variable_to_dict 时用 keys 给出每个变量的键名。',
      '- 本节点只做数据合并，不会向用户输出内容（is_result 无效）。若合并结果要给用户看，必须在其下游接一个「指定回复」或「AI 对话」节点引用合并出的字段；分支最终要给用户的回复，也可直接把各分支 reply 节点设为输出。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前变量聚合节点：聚合方式与分组。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点的输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const strategy = STRATEGIES.includes(String(args.strategy)) ? String(args.strategy) : 'first_non_null'
          const groups = (Array.isArray(args.groups) ? args.groups : []) as Array<Record<string, unknown>>
          if (!groups.length) return new ErrorResult('groups 至少一个分组')
          const names = new Set<string>()
          const groupList = []
          for (const [index, group] of groups.entries()) {
            const field = String(group.field ?? '')
            if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(field)) return new ErrorResult(`groups[${index}].field 不合法：${field}`)
            if (names.has(field)) return new ErrorResult(`组变量名重复：${field}`)
            names.add(field)
            const variables = Array.isArray(group.variables) ? (group.variables as unknown[]) : []
            if (!variables.length) return new ErrorResult(`groups[${index}].variables 至少一个变量`)
            const keys = Array.isArray(group.keys) ? group.keys.map(String) : []
            const variableList = []
            for (const [variableIndex, variable] of variables.entries()) {
              const error = validateReference(context.lf, context.nodeId, variable, `groups[${index}].variables[${variableIndex}]`)
              if (error) return new ErrorResult(error)
              variableList.push({
                v_id: randomId(),
                variable: (variable as unknown[]).map(String),
                ...(strategy === 'variable_to_dict' ? { key: keys[variableIndex] ?? `key${variableIndex + 1}` } : {}),
              })
            }
            groupList.push({ id: randomId(), field, label: String(group.label ?? field), variable_list: variableList })
          }
          writeNodeProperties(node, {
            // 分支汇合需要“任一”前置完成即执行，避免等待未执行的分支导致节点永远不执行
            condition: 'OR',
            node_data: { ...readNodeData<Record<string, unknown>>(node), strategy, group_list: groupList },
            config: {
              ...(node.properties.config as Record<string, unknown>),
              fields: groupList.map((group) => ({ label: group.label, value: group.field })),
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
  description:
    '把多个变量按分组聚合成一个输出；最常用于分支汇合：各分支的输出放进同一组，下游只引用这一组的结果。' +
    '本节点只做数据合并、不向用户输出内容，需要展示时在其下游接「指定回复」或「AI 对话」节点引用合并字段',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
