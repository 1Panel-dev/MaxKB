// 循环引擎自带的输出参数（内置，界面上不展示、不可被用户修改）
export const LOOP_BUILTIN_FIELDS = [
  { field: 'index', label: '下标' },
  { field: 'item', label: '循环元素' },
] as const

export const isLoopBuiltinField = (value?: string) =>
  !!value && LOOP_BUILTIN_FIELDS.some((item) => item.field === value)
