import { getNode, readNodeData, writeNodeProperties } from '@/workflow-canvas/ai-generate/tools/canvas'
import { createUpdateTool, useNodeAgent } from '@/workflow-canvas/ai-generate/tools/node'
import type { JsonObjectSchema, NodeAgentContext, NodeAgentModule } from '@/workflow-canvas/ai-generate/type'

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
}

/** 文本类字段的长度校验规则，与文本配置器一致 */
function textRules(field: FormFieldArgs, required: boolean, minLength: number, maxLength: number) {
  const lengthRule = { min: minLength, max: maxLength, message: `${field.label}长度在 ${minLength} 到 ${maxLength} 个字符`, trigger: 'blur' }
  if (!required) return [lengthRule]
  const requiredRule = field.input_type === 'PasswordInput' ? { required: true, message: `请输入 ${field.label}` } : { whitespace: true, required: true, message: `请输入 ${field.label}` }
  return [requiredRule, lengthRule]
}

function toFormField(field: FormFieldArgs) {
  const required = field.required !== false
  const base = {
    field: field.field,
    label: { label: field.label, input_type: 'TooltipLabel', attrs: { tooltip: field.tooltip ?? '' }, props_info: {} },
    input_type: field.input_type,
    required,
    show_default_value: true,
    visibility_rules: null,
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
      '- form_content_format：展示给用户的引导文字，必须包含占位符 {{form}}（表单渲染位置）。',
      '- 下游可用 [本节点ID, 字段名] 或 {{节点名称.字段名}} 引用各字段。',
    ].join('\n'),
    tools: [
      createUpdateTool(context, config, (args) => {
        const node = getNode(context.lf, context.nodeId)!
        const fields = (Array.isArray(args.fields) ? args.fields : []) as FormFieldArgs[]
        if (!fields.length) return 'fields 至少一个字段'
        const names = new Set<string>()
        for (const field of fields) {
          if (!/^[A-Za-z][A-Za-z0-9_]*$/.test(String(field.field))) return `字段名不合法：${field.field}`
          if (names.has(field.field)) return `字段名重复：${field.field}`
          if (!INPUT_TYPES.includes(field.input_type)) return `input_type 不支持：${field.input_type}`
          if (OPTION_TYPES.includes(field.input_type) && !field.options?.length) return `选项字段 ${field.field} 需要 options`
          if (field.input_type === 'Slider' && Number(field.max ?? 20) <= Number(field.min ?? 0)) return `滑块字段 ${field.field} 的 max 需大于 min`
          names.add(field.field)
        }
        const format =
          typeof args.form_content_format === 'string' && args.form_content_format.includes('{{form}}')
            ? args.form_content_format
            : '你好，请先填写下面表单内容：\n{{form}}\n填写后请点击【提交】按钮进行提交。'
        writeNodeProperties(node, {
          node_data: {
            ...readNodeData<Record<string, unknown>>(node),
            is_result: true,
            form_field_list: fields.map(toFormField),
            form_content_format: format,
          },
          config: {
            ...(node.properties.config as Record<string, unknown>),
            fields: [{ label: '表单全部内容', value: 'form_data' }, ...fields.map((field) => ({ label: field.label, value: field.field }))],
          },
        })
        node.clearNextNodeField(true)
        return null
      }),
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
