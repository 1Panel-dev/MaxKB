export const dynamicFormTypeOptions = [
  { label: 'dynamicForm.types.text', value: 'TextInput' },
  { label: 'dynamicForm.types.textarea', value: 'TextareaInput' },
  { label: 'dynamicForm.types.json', value: 'JsonInput' },
  { label: 'dynamicForm.types.password', value: 'PasswordInput' },
  { label: 'dynamicForm.types.singleSelect', value: 'SingleSelect' },
  { label: 'dynamicForm.types.multiSelect', value: 'MultiSelect' },
  { label: 'dynamicForm.types.radioCard', value: 'RadioCard' },
  { label: 'dynamicForm.types.radioRow', value: 'RadioRow' },
  { label: 'dynamicForm.types.multiRow', value: 'MultiRow' },
  { label: 'dynamicForm.types.slider', value: 'Slider' },
  { label: 'dynamicForm.types.switch', value: 'SwitchInput' },
  { label: 'dynamicForm.types.date', value: 'DatePicker' },
  { label: 'dynamicForm.types.upload', value: 'UploadInput' },
  { label: 'dynamicForm.types.model', value: 'Model' },
  { label: 'dynamicForm.types.knowledge', value: 'Knowledge' },
  { label: 'dynamicForm.types.treeSelect', value: 'TreeSelect' },
] as const

export type DynamicFormInputType = (typeof dynamicFormTypeOptions)[number]['value']
export type DynamicFormTypeOption = (typeof dynamicFormTypeOptions)[number]

// 引用变量为选择类字段提供选项时的格式说明。
export const referenceOptionsHelp = 'dynamicForm.options.referenceSchema'
