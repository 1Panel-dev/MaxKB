/** 解析回答中的 v2 兼容标签：拆成 Markdown 段与标签段，围栏代码块内的标签按原文保留。 */

export const RENDER_TAGS = ['quick_question', 'html_rander', 'iframe_render', 'tool_calls_render', 'echarts_rander', 'form_rander'] as const

export type RenderTag = (typeof RENDER_TAGS)[number]

export interface RenderNode {
  type: 'markdown' | RenderTag
  content: string
}

const TAG_START_PATTERN = new RegExp(`<(${RENDER_TAGS.join('|')})>`, 'g')
const FENCE_START_PATTERN = /^ {0,3}(`{3,}|~{3,})[^\n]*$/gm

/** 返回围栏代码块结束位置；未闭合的围栏延续到全文末尾。 */
function findFenceEnd(source: string, fenceMatch: RegExpExecArray) {
  const fence = fenceMatch[1]!
  const closePattern = new RegExp(`^ {0,3}${fence[0] === '`' ? '`' : '~'}{${fence.length},}[ \\t]*$`, 'gm')
  closePattern.lastIndex = fenceMatch.index + fenceMatch[0].length
  const closeMatch = closePattern.exec(source)
  return closeMatch ? closeMatch.index + closeMatch[0].length : source.length
}

/** 按同名标签嵌套深度查找对应结束标签；找不到返回 -1。 */
function findClosingTag(source: string, tag: RenderTag, contentStart: number) {
  const startTag = `<${tag}>`
  const endTag = `</${tag}>`
  let depth = 1
  let cursor = contentStart
  while (depth > 0) {
    const nextEnd = source.indexOf(endTag, cursor)
    if (nextEnd === -1) return -1
    const nextStart = source.indexOf(startTag, cursor)
    if (nextStart !== -1 && nextStart < nextEnd) {
      depth++
      cursor = nextStart + startTag.length
    } else {
      depth--
      cursor = nextEnd + endTag.length
      if (depth === 0) return nextEnd
    }
  }
  return -1
}

/** 单次扫描，每次处理最先出现的标签，标签内容不再参与其他标签解析。 */
export function parseRenderNodes(source: string): RenderNode[] {
  const nodes: RenderNode[] = []
  let markdownStart = 0
  let cursor = 0
  const pushMarkdown = (end: number) => {
    if (end > markdownStart) nodes.push({ type: 'markdown', content: source.slice(markdownStart, end) })
  }

  while (cursor < source.length) {
    TAG_START_PATTERN.lastIndex = cursor
    const tagMatch = TAG_START_PATTERN.exec(source)
    if (!tagMatch) break

    FENCE_START_PATTERN.lastIndex = cursor
    const fenceMatch = FENCE_START_PATTERN.exec(source)
    if (fenceMatch && fenceMatch.index < tagMatch.index) {
      cursor = findFenceEnd(source, fenceMatch)
      continue
    }

    const tag = tagMatch[1] as RenderTag
    const contentStart = tagMatch.index + tagMatch[0].length
    const contentEnd = findClosingTag(source, tag, contentStart)
    pushMarkdown(tagMatch.index)
    // 标签未闭合（通常是流式输出尚未结束）时先隐藏后续内容，避免露出原始标签
    if (contentEnd === -1) return nodes

    nodes.push({ type: tag, content: source.slice(contentStart, contentEnd) })
    cursor = markdownStart = contentEnd + `</${tag}>`.length
  }

  pushMarkdown(source.length)
  return nodes
}
