import type { DynamicFormValue } from './type'
import type { Dict } from '@/api/types'

// 字段 attrs 来自服务端或对话内容，透传到组件根元素时会被 Vue 当作 DOM 属性赋值。
const BLOCKED_ATTRIBUTE_NAMES = new Set(['innerhtml', 'outerhtml', 'innertext', 'outertext', 'textcontent', 'srcdoc'])
const URL_ATTRIBUTE_NAMES = new Set(['href', 'src', 'action', 'formaction', 'xlink:href'])
const UNSAFE_URL_PATTERN = /^\s*(javascript|vbscript):/i

function isUnsafeAttribute(name: string, value: DynamicFormValue) {
  const attributeName = name.toLowerCase()
  if (BLOCKED_ATTRIBUTE_NAMES.has(attributeName) || attributeName.startsWith('on')) {
    return true
  }
  return URL_ATTRIBUTE_NAMES.has(attributeName) && typeof value === 'string' && UNSAFE_URL_PATTERN.test(value)
}

/** 移除可写入 HTML、绑定事件或执行脚本 URL 的字段属性，其余配置原样保留。 */
export function sanitizeFieldAttrs<T extends Dict<DynamicFormValue>>(attrs?: T | null): T {
  if (!attrs) {
    return {} as T
  }
  return Object.fromEntries(Object.entries(attrs).filter(([name, value]) => !isUnsafeAttribute(name, value))) as T
}
