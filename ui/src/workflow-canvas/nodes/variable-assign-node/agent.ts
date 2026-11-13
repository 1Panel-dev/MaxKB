import { randomId } from '@/utils/common'
import { getFieldOptions, getNode, readNodeData, validateReference, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

const VALUE_TYPES = ['string', 'num', 'json', 'bool']
const SOURCES = ['custom', 'referencing', 'null']

/** variable-assign-node（变量赋值）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    values: {
      type: 'array',
      items: {},
      description: '要赋给变量的上游数据：每个 source=referencing 的赋值项各需要一个引用 [节点ID, 字段]，原样（保持类型）赋给目标变量',
    },
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
          target: { type: 'array', items: { type: 'string' }, description: '被赋值的变量 [分组, 变量名]，分组为 global / chat / loop / output（output 为工具工作流的输出参数）' },
          source: {
            type: 'string',
            enum: SOURCES,
            description:
              '赋值方式：custom 自定义（写死的常量，由 type + value 给出）/ referencing 引用变量（把上游某个字段的值原样赋过来，由 reference 给出）/ null 置空',
          },
          type: {
            type: 'string',
            enum: VALUE_TYPES,
            description: '仅 custom：常量的类型。string 文本 / num 数字 / json 对象或数组 / bool 布尔，默认 string',
          },
          value: {
            description:
              '仅 custom：常量值，须与 type 一致。string 传文本，可含 {{节点名称.字段}}、{{loop.变量名}} 等变量，运行时替换成文本；' +
              'num 传数字；json 传对象 / 数组（或其 JSON 字符串）；bool 传 true / false',
          },
          reference: {
            type: 'array',
            items: { type: 'string' },
            description: '仅 referencing：来源 [节点ID, 字段]，必须是入参 values 里绑定的引用；值按原类型赋值（数组、对象不会被转成文本）',
          },
        },
        required: ['target', 'source'],
      },
      description:
        '赋值列表，每项给一个变量赋值：target 目标变量 + source 赋值方式。' +
        '值是搭建时就确定的常量用 custom；值来自上游节点的输出（尤其是数组、对象或需要保持类型时）用 referencing；清空变量用 null',
    },
  },
  required: ['variables'],
}

const returns: JsonObjectSchema = { type: 'object', properties: {}, additionalProperties: false }

/** 自定义常量按 type 规整成节点表单的存储形式：string 文本、num 数字、json 为 JSON 字符串、bool 布尔 */
function customValueOf(type: string, raw: unknown): { value: unknown } | { error: string } {
  if (raw === undefined || raw === null || raw === '') return { error: '不能为空：自定义赋值需要给出常量值，要置空请用 source="null"' }
  if (type === 'num') {
    const number = typeof raw === 'number' ? raw : Number(raw)
    return Number.isFinite(number) ? { value: number } : { error: `应为数字：${String(raw)}` }
  }
  if (type === 'bool') {
    if (typeof raw === 'boolean') return { value: raw }
    return raw === 'true' || raw === 'false' ? { value: raw === 'true' } : { error: `应为 true / false：${String(raw)}` }
  }
  if (type === 'json') {
    if (typeof raw !== 'string') return { value: JSON.stringify(raw) }
    try {
      JSON.parse(raw)
      return { value: raw }
    } catch {
      return { error: '不是合法的 JSON' }
    }
  }
  return { value: typeof raw === 'string' ? raw : JSON.stringify(raw) }
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'variable-assign-node（变量赋值）配置要点：',
      '- target：要赋值的变量 [分组, 变量名]，分组为 global / chat / loop / output，必须是 get_field_options 里已存在的变量（无法新建变量；循环变量需先在所属 loop-node 的 variables 里声明，工具工作流的输出参数需先在基本信息里声明）。',
      '- source 三选一：',
      '  · custom（自定义）：值是写死的常量，用 type + value 给出。type=string 时 value 是文本，可内嵌 {{节点名称.字段}} / {{loop.变量名}} 等变量，运行时替换后得到的仍是文本；',
      '    type=num 传数字；type=json 传对象或数组；type=bool 传 true / false。',
      '  · referencing（引用变量）：把上游某个字段的值原样赋给目标变量，reference 填已绑定入参 values 中的引用 [节点ID, 字段]；数组、对象等会保持原类型。',
      '  · null：把目标变量置空，不需要 type / value / reference。',
      '- 怎么选：要保持上游数据的类型（数组、对象、数字）或整体搬运上游输出，用 referencing；要写固定值，或把几段文本 / 变量拼成一段文本，用 custom + string。',
      '- 工具工作流的输出参数（target=["output", 参数名]）：工具的返回值只取这里写入的值，其他节点的输出不会自动成为返回值；结果是数组 / 对象时用 referencing 原样赋值，不要用 string 常量拼成文本。',
      '- 循环变量（target=["loop", 变量名]）：本节点必须位于该循环体内。循环变量初始为空，只有本节点能修改它；要累积数据时，用 string 常量拼接旧值与新值（如 "{{loop.变量名}}\\n{{某节点.字段}}"），或先由上游节点算出新值再用 referencing 赋值。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前变量赋值节点：给全局 / 会话 / 循环变量或工具工作流的输出参数赋值。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const variables = Array.isArray(args.variables) ? (args.variables as Array<Record<string, unknown>>) : []
          if (!variables.length) return new ErrorResult('variables 至少一项')
          const groups = getFieldOptions(context.lf, context.nodeId)
          const variableList = []
          for (const [index, variable] of variables.entries()) {
            const target = Array.isArray(variable.target) ? variable.target.map(String) : []
            if (!['global', 'chat', 'loop', 'output'].includes(target[0] ?? ''))
              return new ErrorResult(`variables[${index}].target 只能是 global/chat/loop/output 变量`)
            const error = validateReference(context.lf, context.nodeId, target, `variables[${index}].target`)
            if (error) return new ErrorResult(error)
            const source = SOURCES.includes(String(variable.source)) ? String(variable.source) : 'custom'
            const referencing = source === 'referencing'
            if (referencing) {
              const referenceError = validateReference(context.lf, context.nodeId, variable.reference, `variables[${index}].reference`)
              if (referenceError) return new ErrorResult(referenceError)
            }
            const type = VALUE_TYPES.includes(String(variable.type)) ? String(variable.type) : 'string'
            const value = source === 'custom' ? customValueOf(type, variable.value) : { value: null }
            if ('error' in value) return new ErrorResult(`variables[${index}].value ${value.error}`)
            variableList.push({
              id: randomId(),
              fields: target,
              name: groups.find((group) => group.nodeId === target[0])?.fields.find((field) => field.value === target[1])?.label ?? target[1],
              source,
              type,
              value: value.value,
              reference: referencing ? (variable.reference as unknown[]).map(String) : [],
            })
          }
          writeNodeProperties(node, { node_data: { ...readNodeData<Record<string, unknown>>(node), variable_list: variableList } })
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description:
    '相当于赋值语句：给全局变量 / 会话变量 / 循环变量 / 工具工作流的输出参数赋值，不产生输出。赋值方式有三种：自定义常量、引用上游某个字段的值（保持原类型）、置空。循环变量只能由循环体内的本节点修改：其他节点的输出不会自动写入循环变量，' +
    '需要在产出数据的节点之后接本节点，把上游结果或常量赋给 ["loop", 变量名]。工具工作流的返回值同理：只有本节点写入 ["output", 参数名] 的值才会返回给调用方',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
