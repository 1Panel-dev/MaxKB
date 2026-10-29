import { computed, ref, watch, type Ref } from 'vue'
import { cloneDeep } from 'lodash'
import type { DynamicFormValue, FormField } from '@/components/mk-dynamics-form'
import type { Dict } from '@/api/types'
import type { ConversationAppInfo } from '../../../core/types'

/** 开始节点中旧版简写字段（input / select / date）的配置结构。 */
interface LegacyInputField {
  variable: string
  name?: string
  type?: string
  is_required?: boolean
  default_value?: DynamicFormValue
  optionList?: string[]
  assignment_method?: 'user_input' | 'api_input'
}

interface BaseNodeProperties {
  user_input_field_list?: (FormField | LegacyInputField)[]
  api_input_field_list?: LegacyInputField[]
  input_field_list?: LegacyInputField[]
  user_input_field_list_setting?: { exposed_fields?: string[]; menu_title?: string }
  user_input_config?: { title?: string }
}

// ===== 字段转换 =====
/** 旧版简写字段转为动态表单字段；其他类型视为已是动态表单协议，返回 undefined。 */
function toFormField(inputField: LegacyInputField, label: string, defaultValue?: DynamicFormValue): FormField | undefined {
  const baseField = { field: inputField.variable, label, default_value: defaultValue, required: inputField.is_required }
  switch (inputField.type) {
    case 'input':
      return { ...baseField, input_type: 'TextInput' }
    case 'select':
      return {
        ...baseField,
        input_type: 'SingleSelect',
        option_list: (inputField.optionList || []).map((option) => ({ key: option, value: option })),
      }
    case 'date':
      return {
        ...baseField,
        input_type: 'DatePicker',
        attrs: { format: 'YYYY-MM-DD HH:mm:ss', 'value-format': 'YYYY-MM-DD HH:mm:ss', type: 'datetime' },
      }
    default:
      return undefined
  }
}

function isFormField(field: FormField | undefined): field is FormField {
  return !!field
}

function getLegacyInputFields(properties: BaseNodeProperties, assignmentMethod: LegacyInputField['assignment_method']) {
  return (properties.input_field_list || [])
    .filter((inputField) => inputField.assignment_method === assignmentMethod)
    .map((inputField) => toFormField(inputField, inputField.name || inputField.variable))
    .filter(isFormField)
}

function getUserInputFields(properties: BaseNodeProperties): FormField[] {
  if (!properties.user_input_field_list) {
    return getLegacyInputFields(properties, 'user_input')
  }
  return properties.user_input_field_list.map((inputField) => {
    const legacyField = inputField as LegacyInputField
    return toFormField(legacyField, legacyField.name || legacyField.variable) || (inputField as FormField)
  })
}

function getApiInputFields(properties: BaseNodeProperties): FormField[] {
  if (!properties.api_input_field_list) {
    return getLegacyInputFields(properties, 'api_input')
  }
  // 接口传参以变量名作为标签，并保留配置的默认值
  return properties.api_input_field_list
    .map((inputField) => toFormField(inputField, inputField.variable, inputField.default_value))
    .filter(isFormField)
}

export interface UserFormDeps {
  appInfo: Readonly<Ref<ConversationAppInfo | null>>
  /** 是否在表单中编辑接口传参；仅调试对话开启，其他场景接口传参来自地址栏。 */
  apiInputEditable: boolean
}

/**
 * 用户输入参数状态：字段配置取自开始节点，表单值随消息一起发送。
 * 表单校验依赖已渲染的表单实例，由 user-form 组件挂载时绑定。
 */
export function createUserFormStore(deps: UserFormDeps) {
  const { appInfo, apiInputEditable } = deps

  const formData = ref<Dict<DynamicFormValue>>({})
  const apiFormData = ref<Dict<DynamicFormValue>>({})

  const baseNodeProperties = computed(() => {
    const baseNode = appInfo.value?.work_flow?.nodes?.find((node) => node.id === 'base-node')
    return (baseNode?.properties || {}) as BaseNodeProperties
  })
  const userInputFields = computed(() => getUserInputFields(baseNodeProperties.value))
  const apiInputFields = computed(() => getApiInputFields(baseNodeProperties.value))
  /** 配置为在输入框旁直接展示的字段，实际展示数量由可用宽度决定。 */
  const exposedFieldNames = computed(() => baseNodeProperties.value.user_input_field_list_setting?.exposed_fields || [])
  const menuTitle = computed(
    () => baseNodeProperties.value.user_input_field_list_setting?.menu_title || baseNodeProperties.value.user_input_config?.title || '更多设置',
  )
  const hasFields = computed(() => userInputFields.value.length > 0 || (apiInputEditable && apiInputFields.value.length > 0))

  // 切换智能体后字段不同，清空上一个智能体的参数
  watch(
    () => appInfo.value?.id,
    () => {
      formData.value = {}
      apiFormData.value = {}
    },
  )

  // ===== 校验 =====
  let validator: (() => Promise<unknown>) | null = null
  /** 绑定表单校验，返回解绑函数。 */
  const bindValidator = (validate: () => Promise<unknown>) => {
    validator = validate
    return () => {
      if (validator === validate) validator = null
    }
  }
  const validate = () => (validator ? validator() : Promise.resolve())

  // ===== 编辑快照：取消修改时恢复 =====
  let snapshot: { formData: Dict<DynamicFormValue>; apiFormData: Dict<DynamicFormValue> } | null = null
  const saveSnapshot = () => {
    snapshot = { formData: cloneDeep(formData.value), apiFormData: cloneDeep(apiFormData.value) }
  }
  const restoreSnapshot = () => {
    if (!snapshot) return
    formData.value = snapshot.formData
    apiFormData.value = snapshot.apiFormData
    snapshot = null
  }

  /** 随消息发送的表单数据，接口传参同名时覆盖用户输入。 */
  const getFormData = (): Dict<DynamicFormValue> => ({ ...formData.value, ...apiFormData.value })

  return {
    formData,
    apiFormData,
    userInputFields,
    apiInputFields,
    exposedFieldNames,
    menuTitle,
    hasFields,
    apiInputEditable,
    bindValidator,
    validate,
    saveSnapshot,
    restoreSnapshot,
    getFormData,
  }
}

export type UserFormStore = ReturnType<typeof createUserFormStore>
