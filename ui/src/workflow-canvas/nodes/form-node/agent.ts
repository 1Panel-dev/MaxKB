import { randomId } from '@/utils/common'
import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { finishWithValidate, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import { ErrorResult } from '@/workflow-canvas/ai-generate/tools/result'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'
import type { VisibilityCompareOperator, VisibilityCondition, VisibilityRules } from '@/components/mk-dynamics-form'

/** 可由 AI 生成的字段类型，数据结构与 mk-dynamics-form 各字段配置器的 getData 一致 */
const INPUT_TYPES = [
  'TextInput',
  'TextareaInput',
  'PasswordInput',
  'SingleSelect',
  'MultiSelect',
  'RadioCard',
  'RadioRow',
  'MultiRow',
  'SwitchInput',
  'Slider',
  'DatePicker',
] as const
type FormInputType = (typeof INPUT_TYPES)[number]

const TEXT_TYPES: FormInputType[] = ['TextInput', 'TextareaInput', 'PasswordInput']
const OPTION_TYPES: FormInputType[] = ['SingleSelect', 'MultiSelect', 'RadioCard', 'RadioRow', 'MultiRow']
const MULTI_OPTION_TYPES: FormInputType[] = ['MultiSelect', 'MultiRow']
const DATE_FORMATS: Record<string, string> = { year: 'YYYY', month: 'YYYY-MM', date: 'YYYY-MM-DD', datetime: 'YYYY-MM-DD HH:mm:ss' }

/** 显隐条件的比较运算符，与 VisibilityCompareOperator 一致 */
const COMPARE_OPS: Array<{ label: string; value: VisibilityCompareOperator }> = [
  { label: '等于', value: 'eq' },
  { label: '不等于', value: 'not_eq' },
  { label: '包含', value: 'contain' },
  { label: '不包含', value: 'not_contain' },
  { label: '为真', value: 'is_true' },
  { label: '为假', value: 'is_not_true' },
  { label: '大于', value: 'gt' },
  { label: '大于等于', value: 'ge' },
  { label: '小于', value: 'lt' },
  { label: '小于等于', value: 'le' },
]
const COMPARE_VALUES = COMPARE_OPS.map((op) => op.value)

/** 一条显隐条件的 AI 入参：self=true 时基于本表单另一字段，否则基于上游节点字段 */
interface VisibilityConditionArgs {
  self: boolean
  field: string
  node_id?: string
  compare: VisibilityCompareOperator
  value?: unknown
}

interface VisibilityRulesArgs {
  action: 'show' | 'hide'
  condition: 'and' | 'or'
  conditions: VisibilityConditionArgs[]
}

/** 把 AI 给出的显隐条件构建为节点持久化结构；self 引用指向本表单另一字段，self_ref = [本节点ID, 字段名] */
function toVisibilityRules(rules: VisibilityRulesArgs | undefined, nodeId: string): VisibilityRules | null {
  if (!rules) return null
  const conditions: VisibilityCondition[] = []
  for (const condition of rules.conditions) {
    if (!condition || !condition.field || !condition.compare) continue
    const fieldRef: [string, string] = condition.self ? [nodeId, condition.field] : [condition.node_id ?? '', condition.field]
    if (!fieldRef[0] || !fieldRef[1]) continue
    conditions.push({
      id: randomId(),
      field: fieldRef,
      self: condition.self === true,
      compare: condition.compare,
      value: condition.compare === 'is_true' || condition.compare === 'is_not_true' ? true : (condition.value ?? ''),
    })
  }
  return conditions.length
    ? { action: rules.action === 'hide' ? 'hide' : 'show', condition: rules.condition === 'or' ? 'or' : 'and', conditions }
    : null
}

interface FormFieldArgs {
  field: string
  label: string
  input_type: FormInputType
  required?: boolean
  tooltip?: string
  default_value?: unknown
  options?: string[]
  min_length?: number
  max_length?: number
  min?: number
  max?: number
  step?: number
  date_type?: keyof typeof DATE_FORMATS
  visibility?: VisibilityRulesArgs
}

/** 文本类字段的长度校验规则，与文本配置器一致 */
function textRules(field: FormFieldArgs, required: boolean, minLength: number, maxLength: number) {
  const lengthRule = { min: minLength, max: maxLength, message: `${field.label}长度在 ${minLength} 到 ${maxLength} 个字符`, trigger: 'blur' }
  if (!required) return [lengthRule]
  const requiredRule = field.input_type === 'PasswordInput' ? { required: true, message: `请输入 ${field.label}` } : { whitespace: true, required: true, message: `请输入 ${field.label}` }
  return [requiredRule, lengthRule]
}

function toFormField(field: FormFieldArgs, nodeId: string) {
  const required = field.required !== false
  const base = {
    field: field.field,
    label: { label: field.label, input_type: 'TooltipLabel', attrs: { tooltip: field.tooltip ?? '' }, props_info: {} },
    input_type: field.input_type,
    required,
    show_default_value: true,
    visibility_rules: toVisibilityRules(field.visibility, nodeId),
  }
  if (TEXT_TYPES.includes(field.input_type)) {
    const minLength = Math.max(0, Number(field.min_length ?? 0))
    const maxLength = Math.max(minLength || 1, Number(field.max_length ?? 200))
    const typeAttrs =
      field.input_type === 'TextareaInput' ? { rows: 3 } : field.input_type === 'PasswordInput' ? { type: 'password', 'show-password': true } : {}
    return {
      ...base,
      default_value: field.default_value ?? '',
      attrs: { maxlength: maxLength, minlength: minLength, 'show-word-limit': true, ...typeAttrs },
      props_info: { rules: textRules(field, required, minLength, maxLength) },
    }
  }
  if (OPTION_TYPES.includes(field.input_type)) {
    return {
      ...base,
      attrs: {},
      default_value: field.default_value ?? (MULTI_OPTION_TYPES.includes(field.input_type) ? [] : ''),
      text_field: 'label',
      value_field: 'value',
      assignment_method: 'custom',
      option_list: (field.options ?? []).map((option) => ({ label: option, value: option })),
    }
  }
  if (field.input_type === 'Slider') {
    const min = Number(field.min ?? 0)
    const max = Number(field.max ?? 20)
    return {
      ...base,
      attrs: { min, max, step: Number(field.step ?? 1), 'show-input-controls': true, 'show-input': true },
      props_info: { rules: [{ message: `请输入 ${field.label}`, trigger: 'blur', required }] },
      default_value: field.default_value ?? min,
    }
  }
  if (field.input_type === 'DatePicker') {
    const dateType = field.date_type && DATE_FORMATS[field.date_type] ? field.date_type : 'datetime'
    const format = DATE_FORMATS[dateType]
    return { ...base, attrs: { type: dateType, format, 'value-format': format }, default_value: field.default_value ?? '' }
  }
  return { ...base, attrs: {}, default_value: field.default_value ?? false }
}

/** form-node（表单收集）的 AI 生成配置 */

const params: JsonObjectSchema = { type: 'object', properties: {} }

const config: JsonObjectSchema = {
  type: 'object',
  properties: {
    fields: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          field: { type: 'string' },
          label: { type: 'string' },
          input_type: { type: 'string', enum: [...INPUT_TYPES] },
          required: { type: 'boolean', description: '是否必填，默认 true' },
          tooltip: { type: 'string', description: '字段提示说明（可选）' },
          default_value: { description: '默认值（可选）；多选类为数组，开关为布尔，滑块为数字' },
          options: { type: 'array', items: { type: 'string' }, description: '选项类字段的选项' },
          min_length: { type: 'number', description: '文本类最小长度，默认 0' },
          max_length: { type: 'number', description: '文本类最大长度，默认 200' },
          min: { type: 'number', description: '滑块最小值，默认 0' },
          max: { type: 'number', description: '滑块最大值，默认 20' },
          step: { type: 'number', description: '滑块步长，默认 1' },
          date_type: { type: 'string', enum: Object.keys(DATE_FORMATS), description: '日期粒度，默认 datetime' },
          visibility: {
            type: 'object',
            description: '显隐规则（可选）：根据其他字段的值控制本字段是否显示',
            properties: {
              action: { type: 'string', enum: ['show', 'hide'], description: 'show=满足条件时显示本字段（否则隐藏）；hide=满足条件时隐藏本字段（否则显示）' },
              condition: { type: 'string', enum: ['and', 'or'], description: '多条条件组合方式：and 全部满足 / or 任一满足' },
              conditions: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    self: { type: 'boolean', description: 'true=基于本表单另一字段；false=基于上游节点字段' },
                    field: { type: 'string', description: '被引用的字段名：self=true 时为本表单另一字段名，否则为上游字段名' },
                    node_id: { type: 'string', description: 'self=false 时上游节点 id' },
                    compare: { type: 'string', enum: [...COMPARE_VALUES], description: '比较方式' },
                    value: { description: '比较值：is_true / is_not_true 时可不填，其余按字段类型给值' },
                  },
                  required: ['self', 'field', 'compare'],
                },
              },
            },
            required: ['action', 'condition', 'conditions'],
          },
        },
        required: ['field', 'label', 'input_type'],
      },
      description: '要收集的表单字段：field 英文变量名，label 显示名，input_type 控件类型',
    },
    form_content_format: { type: 'string', description: '引导文字，含 {{form}}' },
  },
  required: ['fields'],
}

const returns: JsonObjectSchema = {
  type: 'object',
  properties: {
    form_data: { type: 'object', description: '表单全部内容（字段名 → 填写值）' },
  },
  additionalProperties: {
    description: '每个表单字段一个返回字段：字段名为 config.fields[].field；类型按控件：开关 boolean、滑块 number、多选 array，其余 string',
    'x-from': 'fields',
  },
}

function useAgent(context: NodeAgentContext) {
  return useNodeAgent(context, {
    prompt: [
      'form-node（表单收集）配置要点：',
      '- fields：要收集的字段，field 为英文变量名（字母开头，下划线分隔），label 为中文显示名。',
      '- input_type：文本 TextInput / 多行文本 TextareaInput / 密码 PasswordInput；单选下拉 SingleSelect / 多选下拉 MultiSelect / 选项卡 RadioCard / 单行选项卡 RadioRow / 单行多选卡 MultiRow（选项类需给 options）；开关 SwitchInput；滑块 Slider（min / max / step）；日期 DatePicker（date_type）。',
      '- 可选：required（默认必填）、tooltip 提示、default_value 默认值、文本类 min_length / max_length。',
      '- visibility：显隐规则（可选）。action：show=满足条件时显示本字段，hide=满足条件时隐藏本字段。想“满足某条件就把字段藏起来”用 hide；想“满足某条件才显示”用 show。',
      '- form_content_format：展示给用户的引导文字，必须包含占位符 {{form}}（表单渲染位置）。',
      '- 下游可用 [本节点ID, 字段名] 或 {{节点名称.字段名}} 引用各字段。',
    ].join('\n'),
    tools: [
      {
        name: 'update',
        description:
          '配置当前表单收集节点：字段列表 fields（含显隐 visibility）、引导文字 form_content_format。只传要设置的字段，其余保持不变。' +
          '写入后自动校验，通过即配置完成并交付本节点输出字段；不通过返回 error 继续修。',
        parameters: config,
        apply: async (args) => {
          const node = getNode(context.lf, context.nodeId)
          if (!node) return new ErrorResult(`节点不存在: ${context.nodeId}`)
          const fields = (Array.isArray(args.fields) ? args.fields : []) as FormFieldArgs[]
          if (!fields.length) return new ErrorResult('fields 至少一个字段')
          const names = new Set<string>()
          for (const field of fields) {
            if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(String(field.field))) return new ErrorResult(`字段名不合法：${field.field}`)
            if (names.has(field.field)) return new ErrorResult(`字段名重复：${field.field}`)
            if (!INPUT_TYPES.includes(field.input_type)) return new ErrorResult(`input_type 不支持：${field.input_type}`)
            if (OPTION_TYPES.includes(field.input_type) && !field.options?.length) return new ErrorResult(`选项字段 ${field.field} 需要 options`)
            if (field.input_type === 'Slider' && Number(field.max ?? 20) <= Number(field.min ?? 0)) {
              return new ErrorResult(`滑块字段 ${field.field} 的 max 需大于 min`)
            }
            names.add(field.field)
          }
          for (const field of fields) {
            for (const condition of field.visibility?.conditions ?? []) {
              if (!COMPARE_VALUES.includes(condition.compare)) return new ErrorResult(`字段 ${field.field} 显隐比较符不支持：${condition.compare}`)
              if (condition.self !== true && !condition.node_id) return new ErrorResult(`字段 ${field.field} 的显隐条件 self=false 需给 node_id`)
              if (condition.self === true && !names.has(condition.field)) {
                return new ErrorResult(`字段 ${field.field} 的显隐 self 字段不存在：${condition.field}（只能引用本表单已定义字段）`)
              }
            }
          }
          const format =
            typeof args.form_content_format === 'string' && args.form_content_format.includes('{{form}}')
              ? args.form_content_format
              : '你好，请先填写下面表单内容：\n{{form}}\n填写后请点击【提交】按钮进行提交。'
          writeNodeProperties(node, {
            node_data: {
              ...readNodeData<Record<string, unknown>>(node),
              is_result: true,
              form_field_list: fields.map((field) => toFormField(field, node.id)),
              form_content_format: format,
            },
            config: {
              ...(node.properties.config as Record<string, unknown>),
              fields: [{ label: '表单全部内容', value: 'form_data' }, ...fields.map((field) => ({ label: field.label, value: field.field }))],
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
  description: '向用户展示表单并等待提交，提交后流程继续；用于先收集信息（报名、工单、预约）再处理，下游以 {{表单节点名称.字段名}} 引用填写值',
  params,
  config,
  returns,
  useAgent,
} satisfies NodeAgentModule
