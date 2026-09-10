import { get, set } from 'lodash'
import { RESOURCE_TYPE, TRIGGER_PARAMETER_SOURCE } from '@/api/enums'
import type { ApplicationDetail, ToolItem, TriggerParameter, TriggerParameters, TriggerTaskSource } from '@/api/types'

export interface TaskParameterField {
  path: string[]
  label: string
  required: boolean
  defaultValue: string
}

/** 根据资源输入定义生成触发任务参数，兼容普通工具和工作流工具。 */
export function getTaskParameterFields(source: TriggerTaskSource, resource?: Partial<ApplicationDetail & ToolItem>): TaskParameterField[] {
  const fields: TaskParameterField[] = []
  const isApplication = source === RESOURCE_TYPE.APPLICATION
  const baseNode = resource?.work_flow?.nodes?.find((node) => node.type === (isApplication ? 'base-node' : 'tool-base-node'))
  const properties = baseNode?.properties ?? {}
  if (isApplication) {
    fields.push({ path: ['question'], label: '问题', required: true, defaultValue: '' })
    const nodeData = properties.node_data ?? {}
    if (nodeData.file_upload_enable) {
      const fileLabels = { document: '文档', image: '图片', audio: '音频', video: '视频', other: '其他文件' }
      Object.entries(fileLabels).forEach(([type, label]) => {
        if (nodeData.file_upload_setting?.[type]) fields.push({ path: [`${type}_list`], label, required: true, defaultValue: '[]' })
      })
    }
  } else {
    resource?.input_field_list?.forEach((field) => {
      fields.push({ path: [field.name], label: field.name, required: field.is_required, defaultValue: '' })
    })
  }
  const userFields = properties.user_input_field_list as
    | { field: string; required?: boolean; is_required?: boolean; default_value?: unknown; label?: string | { label?: string } }[]
    | undefined
  userFields?.forEach((field) => {
    fields.push({
      path: ['user_input_field_list', field.field],
      label: typeof field.label === 'string' ? field.label : field.label?.label || field.field,
      required: field.required ?? field.is_required ?? false,
      defaultValue:
        typeof field.default_value === 'string' ? field.default_value : field.default_value === undefined ? '' : JSON.stringify(field.default_value),
    })
  })
  if (isApplication) {
    const apiFields = properties.api_input_field_list as { variable: string; is_required?: boolean }[] | undefined
    apiFields?.forEach((field) =>
      fields.push({ path: ['api_input_field_list', field.variable], label: field.variable, required: field.is_required ?? false, defaultValue: '' }),
    )
  }
  return fields
}

/** 只补全缺失输入，编辑和折叠时不覆盖已保存参数。 */
export function initializeTaskParameters(parameters: TriggerParameters, fields: TaskParameterField[]) {
  fields.forEach((field) => {
    if (!get(parameters, field.path)) set(parameters, field.path, { source: TRIGGER_PARAMETER_SOURCE.CUSTOM, value: field.defaultValue })
  })
  return parameters
}

export function getTaskParameter(parameters: TriggerParameters, field: TaskParameterField): TriggerParameter {
  return get(parameters, field.path) as TriggerParameter
}
