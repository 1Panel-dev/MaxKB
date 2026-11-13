import { cloneDeep } from 'lodash'
import { getNode, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { AgentSuccessResult, ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import { WorkflowNodeType } from '@/workflow-canvas/types'
import type { ToolInputField, ToolOutputField } from './types'

/**
 * tool-base-node（工具基本信息）的 AI 生成配置：声明工具工作流的函数签名。
 * 输入参数写入 properties.user_input_field_list（开始节点提供为全局变量 global），
 * 输出参数写入 properties.user_output_field_list（流程内由变量赋值写入 output）。
 */

const INPUT_TYPES = ['string', 'int', 'float', 'boolean', 'dict', 'array']
const FIELD_PATTERN = /^[A-Za-z_][A-Za-z0-9_]{0,63}$/
const FIELD_DESCRIPTION = '参数名：字母、数字、下划线，不以数字开头，最长 64'

const params: JsonObjectSchema = { type: 'object', properties: {} }

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    inputs: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string', description: FIELD_DESCRIPTION },
          label: { type: 'string', description: '显示名称（简短）' },
          type: { type: 'string', enum: INPUT_TYPES, description: '数据类型：文本 string，列表 array，对象 dict' },
          desc: { type: 'string', description: '参数说明，最长 128 字：含义、格式与示例。智能体调用工具时模型只靠它决定传什么' },
          is_required: { type: 'boolean', description: '是否必填，默认 true' },
        },
        required: ['field', 'label', 'type', 'desc'],
      },
      description: '输入参数：调用方传入，流程内用 ["global", 参数名] 引用。整体替换，省略则保持不变',
    },
    outputs: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string', description: FIELD_DESCRIPTION },
          label: { type: 'string', description: '显示名称（简短）' },
        },
        required: ['field', 'label'],
      },
      description: '输出参数：工具的返回字段，流程内由变量赋值节点写入 ["output", 参数名]。整体替换，省略则保持不变',
    },
  },
}

const returns: JsonObjectSchema = { type: 'object', properties: {}, additionalProperties: false }

function fieldsOf<T>(context: NodeAgentContext, key: 'user_input_field_list' | 'user_output_field_list'): T[] {
  const fields = getNode(context.lf, context.nodeId)?.properties[key]
  return Array.isArray(fields) ? (fields as T[]) : []
}

/** 当前签名：交付给父 agent，也写进配置 agent 的提示词（参数存在 properties 顶层，不在 node_data 里） */
function signatureOf(context: NodeAgentContext) {
  return {
    inputs: fieldsOf<ToolInputField>(context, 'user_input_field_list').map((field) => ({
      field: field.field,
      label: field.label,
      type: field.type,
      is_required: field.is_required,
      desc: field.desc,
      ref: ['global', field.field],
    })),
    outputs: fieldsOf<ToolOutputField>(context, 'user_output_field_list').map((field) => ({ field: field.field, label: field.label, ref: ['output', field.field] })),
  }
}

function parseFields(raw: unknown, label: string): Array<Record<string, unknown>> | string {
  if (!Array.isArray(raw)) return `${label} 应为数组`
  const names = new Set<string>()
  for (const [index, item] of raw.entries()) {
    const field = String((item as Record<string, unknown> | null)?.field ?? '')
    if (!FIELD_PATTERN.test(field)) return `${label}[${index}].field 不合法：${field || '（空）'}。${FIELD_DESCRIPTION}`
    if (names.has(field)) return `${label} 参数名重复：${field}`
    names.add(field)
  }
  return raw as Array<Record<string, unknown>>
}

const trimmed = (value: unknown) => String(value ?? '').trim()

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'tool-base-node（工具基本信息）配置要点：声明工具工作流的函数签名，即输入参数与输出参数。',
      '- 严格按父 agent 的要求声明：参数名、类型、是否必填照要求写，不要自行增删参数或改名（流程里的节点按参数名引用）。',
      '- inputs（输入参数）：调用方传入的数据。type 按数据形态选：文本 string，数字 int / float，开关 boolean，列表 array，对象 dict。',
      '- desc 是写给调用方的：智能体调用工具时，模型只能看到每个输入参数的 desc 并据此生成参数值，要写清含义、格式与示例，不超过 128 字；被工作流节点调用时写清需要什么结构的数据。',
      '- outputs（输出参数）：工具的返回字段，只需参数名与显示名称；它的值由流程里的变量赋值节点写入。',
      '- 输入参数和输出参数都可以没有：要求里没提到的一侧不要自行添加；要清空某一侧时传空数组。',
      '- inputs / outputs 各自整体替换：修改其中一项时要带上该侧要保留的其余参数；只改一侧时另一侧省略。',
      `当前签名：${JSON.stringify(signatureOf(context))}`,
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '声明工具的输入参数与输出参数。inputs / outputs 各自整体替换（以传入的列表为准），省略的一侧保持不变。写入成功即配置完成，交付最新签名。',
        parameters: config,
        apply: (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          if (args.inputs === undefined && args.outputs === undefined) return new ErrorResult('inputs 与 outputs 至少传一个')
          const properties: Record<string, unknown> = {}
          if (args.inputs !== undefined) {
            const inputs = parseFields(args.inputs, 'inputs')
            if (typeof inputs === 'string') return new ErrorResult(inputs)
            for (const [index, input] of inputs.entries()) {
              if (!INPUT_TYPES.includes(String(input.type))) return new ErrorResult(`inputs[${index}].type 只能是 ${INPUT_TYPES.join(' / ')}`)
              if (!trimmed(input.label)) return new ErrorResult(`inputs[${index}].label 不能为空`)
              if (trimmed(input.label).length > 128) return new ErrorResult(`inputs[${index}].label 超过 128 字`)
              if (trimmed(input.desc).length > 128) return new ErrorResult(`inputs[${index}].desc 超过 128 字，请精简`)
            }
            properties.user_input_field_list = inputs.map(
              (input): ToolInputField => ({
                field: String(input.field),
                label: trimmed(input.label),
                type: String(input.type),
                desc: trimmed(input.desc),
                is_required: input.is_required !== false,
              }),
            )
          }
          if (args.outputs !== undefined) {
            const outputs = parseFields(args.outputs, 'outputs')
            if (typeof outputs === 'string') return new ErrorResult(outputs)
            const existing = new Map(fieldsOf<ToolOutputField>(context, 'user_output_field_list').map((field) => [field.field, field]))
            properties.user_output_field_list = outputs.map(
              (output): ToolOutputField => ({
                type: 'string',
                is_required: true,
                ...cloneDeep(existing.get(String(output.field)) ?? {}),
                field: String(output.field),
                label: trimmed(output.label).slice(0, 128) || String(output.field),
              }),
            )
          }
          writeNodeProperties(node, properties)
          // 开始节点的全局变量来自输入参数：直接同步，不依赖开始节点视图是否已挂载
          const startNode = getNode(context.lf, WorkflowNodeType.ToolStartNode)
          if (startNode) {
            writeNodeProperties(startNode, {
              config: {
                ...((startNode.properties.config as Record<string, unknown> | undefined) ?? {}),
                globalFields: fieldsOf<ToolInputField>(context, 'user_input_field_list').map((field) => ({ label: field.label || field.field, value: field.field })),
              },
            })
            context.lf.graphModel.eventCenter.emit('refreshFieldList', undefined)
            startNode.clearNextNodeField(true)
          }
          return new AgentSuccessResult({
            ...signatureOf(context),
            note: '改名或删除过参数时，引用旧参数的节点需要重新配置；validate 会列出仍引用未声明参数的位置',
          })
        },
      },
    ],
  })
}

export default {
  description: '工具工作流的函数签名：声明输入参数（调用方传入，流程内引用 ["global", 参数名]）与输出参数（工具返回字段，由变量赋值写入 ["output", 参数名]）',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
