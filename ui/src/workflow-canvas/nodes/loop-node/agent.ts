import { getLoopBodyLf, getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { isLoopBuiltinField } from '@/workflow-canvas/nodes/loop-start-node/constant'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import { argReference, finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

/** loop-node（循环）的 AI 生成配置 */

const params: JsonObjectSchema = {
  type: 'object',
  properties: {
    array: { type: 'array', description: 'ARRAY 模式遍历的数组', 'x-bind': 'array' },
  },
}

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    loop_type: { type: 'string', enum: ['ARRAY', 'NUMBER', 'LOOP'], description: 'ARRAY 遍历入参 array，NUMBER 固定次数，LOOP 无限循环' },
    number: { type: 'number', description: 'NUMBER 时的次数' },
    variables: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string', description: '变量名，只能包含英文字母、数字、下划线，不能用内置的 index / item' },
          label: { type: 'string', description: '显示名称' },
        },
        required: ['field', 'label'],
      },
      description:
        '循环变量：声明在循环体的 loop-start-node 上，用于跨轮次累积 / 传递数据（如累加结果、收集每轮输出）。传入即整体替换，不传保持不变。' +
        '循环体内用 ["loop", 变量名] 引用、提示词写 {{loop.变量名}}；初始为空，只能由循环体内的变量赋值节点（target=["loop", 变量名]）修改；循环结束后下游用 [循环节点ID, 变量名] 引用其最终值',
    },
  },
  required: ['loop_type'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {},
  additionalProperties: { type: 'any', description: '循环变量的最终值：循环结束后下游以 [循环节点ID, 变量名] 引用', 'x-from': 'variables' },
}

interface LoopVariable {
  field: string
  label: string
}

/** 规整并校验循环变量；返回错误文本或规整后的列表 */
function normalizeVariables(raw: unknown): LoopVariable[] | string {
  if (!Array.isArray(raw)) return 'variables 应为数组'
  const variables: LoopVariable[] = []
  for (const [index, item] of raw.entries()) {
    const field = String((item as Partial<LoopVariable> | null)?.field ?? '').trim()
    const label = String((item as Partial<LoopVariable> | null)?.label ?? '').trim() || field
    if (!/^[a-zA-Z0-9_]+$/.test(field)) return `variables[${index}].field 只能包含英文字母、数字、下划线`
    if (isLoopBuiltinField(field)) return `variables[${index}].field 不能使用循环内置参数 ${field}`
    if (variables.some((variable) => variable.field === field)) return `循环变量重复：${field}`
    variables.push({ field, label })
  }
  return variables
}

/** 循环变量存放在循环体 loop-start-node 的 loop_input_field_list，并同步为循环节点的输出字段（与循环开始节点表单一致） */
async function writeLoopVariables(context: NodeAgentContext, variables: LoopVariable[]): Promise<string | null> {
  const node = getNode(context.lf, context.nodeId)
  const bodyLf = await getLoopBodyLf(context.lf, context.nodeId)
  const startNode = bodyLf ? getNode(bodyLf, WorkflowNodeType.LoopStartNode) : undefined
  if (!node || !startNode) return '循环体尚未就绪，无法写入循环变量，请稍后重试'
  writeNodeProperties(startNode, { loop_input_field_list: variables.map((variable) => ({ ...variable })) })
  startNode.clearNextNodeField(true)
  const nodeConfig = (node.properties.config ?? {}) as Record<string, unknown>
  writeNodeProperties(node, { config: { ...nodeConfig, fields: variables.map((variable) => ({ label: variable.label, value: variable.field })) } })
  node.clearNextNodeField(true)
  return null
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'loop-node（循环）配置要点：只配循环本身，循环体由建图 agent 另行搭建。',
      '- loop_type：ARRAY 遍历已绑定入参 array；NUMBER 循环 number 次；LOOP 无限循环（循环体内必须放 Break）。',
      '- variables：需要跨轮次累积 / 传递数据，或循环结束后还要用到循环内算出的值时，声明循环变量；要求了返回字段时，返回字段名就是循环变量名。不需要则不传。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前循环节点：循环类型 loop_type、次数 number 与循环变量 variables。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const loopType = String(args.loop_type)
          if (!['ARRAY', 'NUMBER', 'LOOP'].includes(loopType)) return new ErrorResult(`loop_type 不合法：${loopType}`)
          const array = argReference(context, 'array')
          if (loopType === 'ARRAY' && !array) return new ErrorResult('ARRAY 模式需要父节点传入入参 array，请改用 NUMBER / LOOP 或说明缺少该入参')
          const variables = args.variables === undefined ? undefined : normalizeVariables(args.variables)
          if (typeof variables === 'string') return new ErrorResult(variables)
          writeNodeProperties(node, {
            node_data: {
              ...readNodeData<Record<string, unknown>>(node),
              loop_type: loopType,
              array: loopType === 'ARRAY' && array ? [...array] : [],
              number: loopType === 'NUMBER' ? Math.max(1, Number(args.number ?? 1)) : 1,
            },
          })
          if (variables) {
            const error = await writeLoopVariables(context, variables)
            if (error) return new ErrorResult(error)
          }
          return finishWithValidate(context)
        },
      },
    ],
  })
}

export default {
  description:
    '相当于 for：ARRAY 遍历数组、NUMBER 固定次数、LOOP 无限循环（循环体内必须放 Break）。循环体在 lf_id=该循环节点 id 的画布中搭建，' +
    '首节点接 loop-start-node，以 [loop-start-node, item] / [loop-start-node, index] 取当前元素与下标；要遍历的数组常由参数提取的 array 参数产出。' +
    '可声明循环变量（相当于循环外定义、循环内更新的变量）：循环体内用 ["loop", 变量名] 读，各轮共享；修改它只能在循环体内放变量赋值节点（variable-assign-node），其他节点的输出不会自动写入；' +
    '循环结束后其最终值作为本节点的返回字段，下游以 [循环节点ID, 变量名] 引用',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
