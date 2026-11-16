export const dynamicFormTypeOptions = [
  { label: '文本框', value: 'TextInput' },
  { label: '多行文本框', value: 'TextareaInput' },
  { label: 'JSON 文本框', value: 'JsonInput' },
  { label: '密码框', value: 'PasswordInput' },
  { label: '单选框', value: 'SingleSelect' },
  { label: '多选框', value: 'MultiSelect' },
  { label: '选项卡', value: 'RadioCard' },
  { label: '单行选项卡', value: 'RadioRow' },
  { label: '单行多选卡', value: 'MultiRow' },
  { label: '滑块', value: 'Slider' },
  { label: '开关', value: 'SwitchInput' },
  { label: '日期', value: 'DatePicker' },
  { label: '文件上传', value: 'UploadInput' },
  { label: '模型', value: 'Model' },
  { label: '知识库', value: 'Knowledge' },
  { label: '树形选择器', value: 'TreeSelect' },
] as const

export type DynamicFormInputType = (typeof dynamicFormTypeOptions)[number]['value']
export type DynamicFormTypeOption = (typeof dynamicFormTypeOptions)[number]

// 引用变量为选择类字段提供选项时的格式说明。
export const referenceOptionsHelp = `变量的值必须符合:
[
  {
    "label": "xx",
    "value": "xx",
    "default": false
  }
]
label: 标签 必填
value: 值 必填
default: 是否为默认值`

/** 控件类型的展示翻译 key；不写入字段配置。 */
export const DYNAMIC_FORM_TYPE_MESSAGE_KEYS: Record<string, string> = {
  TextInput: 'dynamicForm.types.textInput',
  TextareaInput: 'dynamicForm.types.textareaInput',
  JsonInput: 'dynamicForm.types.jsonInput',
  PasswordInput: 'dynamicForm.types.passwordInput',
  SingleSelect: 'dynamicForm.types.singleSelect',
  MultiSelect: 'dynamicForm.types.multiSelect',
  RadioCard: 'dynamicForm.types.radioCard',
  RadioRow: 'dynamicForm.types.radioRow',
  MultiRow: 'dynamicForm.types.multiRow',
  Slider: 'dynamicForm.types.slider',
  SwitchInput: 'dynamicForm.types.switchInput',
  DatePicker: 'dynamicForm.types.datePicker',
  UploadInput: 'dynamicForm.types.uploadInput',
  Model: 'dynamicForm.types.model',
  Knowledge: 'dynamicForm.types.knowledge',
  TreeSelect: 'dynamicForm.types.treeSelect',
}
