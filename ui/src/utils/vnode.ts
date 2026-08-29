/** 提供 Vue 插槽 VNode 内容判断。 */

import { Comment, Fragment, isVNode, Text } from 'vue'

/** 判断插槽输出是否包含可渲染内容，忽略空白文本、注释和空 Fragment。 */
export function hasRenderableSlotContent(children: unknown): boolean {
  const childNodes = Array.isArray(children) ? children : [children]

  return childNodes.some((child) => {
    if (!isVNode(child)) return child != null && String(child).trim().length > 0
    if (child.type === Comment) return false
    if (child.type === Text) return String(child.children ?? '').trim().length > 0
    if (child.type === Fragment) return hasRenderableSlotContent(child.children)
    return true
  })
}
