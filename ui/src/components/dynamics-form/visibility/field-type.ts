export type InferredFieldType = string | undefined

export function inferFieldType(
  fieldPath: [string, string] | Array<string>,
  nodeModel: any,
  currentNodeFields?: Array<any>,
): InferredFieldType {
  return getFieldConfig(fieldPath, nodeModel, currentNodeFields)?.input_type
}

// input_type → 允许的运算符（按设计文档表格）
const TYPE_OP_MAP: Record<string, Array<string>> = {
  SwitchInput: ['is_true', 'is_not_true'],

  SingleSelect: ['eq', 'not_eq'],
  RadioCard: ['eq', 'not_eq'],
  RadioRow: ['eq', 'not_eq'],
  TreeSelect: ['eq', 'not_eq'],
  Model: ['eq', 'not_eq'],
  Knowledge: ['eq', 'not_eq'],
  DatePicker: ['eq', 'not_eq'],

  MultiSelect: ['contain', 'not_contain'],
  MultiRow: ['contain', 'not_contain'],

  TextInput: ['eq', 'not_eq', 'contain', 'not_contain'],
  TextareaInput: ['eq', 'not_eq', 'contain', 'not_contain'],
  PasswordInput: ['eq', 'not_eq', 'contain', 'not_contain'],
  JsonInput: ['eq', 'not_eq', 'contain', 'not_contain'],

  Slider: ['eq', 'not_eq', 'gt', 'ge', 'lt', 'le'],
}

const ALL_VISIBILITY_OPS = [
  'eq',
  'not_eq',
  'contain',
  'not_contain',
  'is_true',
  'is_not_true',
  'gt',
  'ge',
  'lt',
  'le',
]

export function getAllowedOps(inputType: string | undefined): Array<string> {
  if (!inputType) return ALL_VISIBILITY_OPS
  return TYPE_OP_MAP[inputType] ?? ALL_VISIBILITY_OPS
}

/**
 * 根据 [node_id, field_name] 取回完整字段配置对象。
 * 推不出 → 返回 undefined
 */
export function getFieldConfig(
  fieldPath: [string, string] | Array<string>,
  nodeModel: any,
  currentNodeFields?: Array<any>,
): any | undefined {
  if (!fieldPath || fieldPath.length < 2) return undefined
  const [nodeId, fieldName] = fieldPath

  if (nodeId === nodeModel?.id) {
    return (currentNodeFields ?? []).find((f: any) => f.field === fieldName)
  }
  const targetNode = nodeModel?.graphModel?.getNodeModelById?.(
    nodeId === 'global' ? 'base-node' : nodeId,
  )
  if (!targetNode) return undefined

  let fieldList: Array<any> = []
  if (targetNode.type === 'form-node') {
    fieldList = targetNode.properties?.node_data?.form_field_list ?? []
  } else if (targetNode.type === 'base-node') {
    fieldList = targetNode.properties?.user_input_field_list ?? []
  }
  return fieldList.find((item: any) => item.field === fieldName)
}
