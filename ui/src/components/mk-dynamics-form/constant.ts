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
