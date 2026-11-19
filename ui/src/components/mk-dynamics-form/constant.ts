import { computed, reactive } from 'vue'
import { t } from '@/locales'
/** 动态表单控件类型的有序定义；label 随语言更新，不写入字段配置。 */
export const DYNAMIC_FORM_TYPES = reactive([
  { value: 'TextInput', label: computed(() => t('dynamicForm.types.textInput')) },
  { value: 'TextareaInput', label: computed(() => t('dynamicForm.types.textareaInput')) },
  { value: 'JsonInput', label: computed(() => t('dynamicForm.types.jsonInput')) },
  { value: 'PasswordInput', label: computed(() => t('dynamicForm.types.passwordInput')) },
  { value: 'SingleSelect', label: computed(() => t('dynamicForm.types.singleSelect')) },
  { value: 'MultiSelect', label: computed(() => t('dynamicForm.types.multiSelect')) },
  { value: 'RadioCard', label: computed(() => t('dynamicForm.types.radioCard')) },
  { value: 'RadioRow', label: computed(() => t('dynamicForm.types.radioRow')) },
  { value: 'MultiRow', label: computed(() => t('dynamicForm.types.multiRow')) },
  { value: 'Slider', label: computed(() => t('dynamicForm.types.slider')) },
  { value: 'SwitchInput', label: computed(() => t('dynamicForm.types.switchInput')) },
  { value: 'DatePicker', label: computed(() => t('dynamicForm.types.datePicker')) },
  { value: 'UploadInput', label: computed(() => t('dynamicForm.types.uploadInput')) },
  { value: 'Model', label: computed(() => t('dynamicForm.types.model')) },
  { value: 'Knowledge', label: computed(() => t('dynamicForm.types.knowledge')) },
  { value: 'TreeSelect', label: computed(() => t('dynamicForm.types.treeSelect')) },
] as const)

export type DynamicFormInputType = (typeof DYNAMIC_FORM_TYPES)[number]['value']
export type DynamicFormTypeOption = (typeof DYNAMIC_FORM_TYPES)[number]

const selectionFieldTypes = new Set(
  [
    'SingleSelect',
    'MultiSelect',
    'Radio',
    'RadioCard',
    'RadioRow',
    'MultiRow',
    'SwitchInput',
    'TreeSelect',
    'Tree',
    'DatePicker',
    'Model',
    'Knowledge',
    'UploadInput',
  ].map((type) => type.toUpperCase()),
)

/** 必填提示按实际控件区分输入与选择，与运行时控件匹配一样忽略大小写。 */
export function isSelectionFieldType(inputType: string) {
  return selectionFieldTypes.has(inputType.toUpperCase())
}
