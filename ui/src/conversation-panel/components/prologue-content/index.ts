/** 开场白：把列表项转换为快捷问题（与 v2 一致）。 */

import { parseRenderNodes } from '../markdown-renderer/parse-tags'

const FENCE_PATTERN = /^ {0,3}(`{3,}|~{3,})/
const LIST_ITEM_PATTERN = /^\s*-\s+(.+?)\s*$/

/** 正文中以 "- " 开头的行转为快捷问题；标签内容与围栏代码块保持原样。 */
export function formatPrologue(prologue: string): string {
  return parseRenderNodes(prologue)
    .map((node) => {
      if (node.type !== 'markdown') return `<${node.type}>${node.content}</${node.type}>`
      let inFence = false
      return node.content
        .split('\n')
        .map((line) => {
          if (FENCE_PATTERN.test(line)) inFence = !inFence
          const listItem = inFence ? null : LIST_ITEM_PATTERN.exec(line)
          return listItem ? `<quick_question>${listItem[1]}</quick_question>` : line
        })
        .join('\n')
    })
    .join('')
}
