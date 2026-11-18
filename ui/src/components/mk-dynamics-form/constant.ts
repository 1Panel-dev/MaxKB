/** 动态表单控件类型的有序定义；展示时翻译 labelKey，不写入字段配置。 */
export const DYNAMIC_FORM_TYPES = [
  { value: 'TextInput', labelKey: 'dynamicForm.types.textInput' },
  { value: 'TextareaInput', labelKey: 'dynamicForm.types.textareaInput' },
  { value: 'JsonInput', labelKey: 'dynamicForm.types.jsonInput' },
  { value: 'PasswordInput', labelKey: 'dynamicForm.types.passwordInput' },
  { value: 'SingleSelect', labelKey: 'dynamicForm.types.singleSelect' },
  { value: 'MultiSelect', labelKey: 'dynamicForm.types.multiSelect' },
  { value: 'RadioCard', labelKey: 'dynamicForm.types.radioCard' },
  { value: 'RadioRow', labelKey: 'dynamicForm.types.radioRow' },
  { value: 'MultiRow', labelKey: 'dynamicForm.types.multiRow' },
  { value: 'Slider', labelKey: 'dynamicForm.types.slider' },
  { value: 'SwitchInput', labelKey: 'dynamicForm.types.switchInput' },
  { value: 'DatePicker', labelKey: 'dynamicForm.types.datePicker' },
  { value: 'UploadInput', labelKey: 'dynamicForm.types.uploadInput' },
  { value: 'Model', labelKey: 'dynamicForm.types.model' },
  { value: 'Knowledge', labelKey: 'dynamicForm.types.knowledge' },
  { value: 'TreeSelect', labelKey: 'dynamicForm.types.treeSelect' },
] as const

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
