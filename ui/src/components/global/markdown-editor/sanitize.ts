import createDOMPurify from 'dompurify'

// 使用独立实例，避免影响上标浮层等其他 DOMPurify 调用。
const markdownPurifier = createDOMPurify(window)

markdownPurifier.addHook('uponSanitizeAttribute', (node, attribute) => {
  if (!['video', 'audio', 'source'].includes(node.nodeName.toLowerCase())) return

  if (['src', 'poster'].includes(attribute.attrName)) {
    try {
      const resourceUrl = new URL(attribute.attrValue, window.location.href)
      attribute.keepAttr = ['http:', 'https:', 'blob:'].includes(resourceUrl.protocol)
    } catch {
      attribute.keepAttr = false
    }
  }

  if (attribute.attrName === 'preload' && !['none', 'metadata'].includes(attribute.attrValue)) {
    attribute.attrValue = 'metadata'
  }
})

/** 清洗 Markdown 最终输出，保留引用、媒体及公式和图表所需的 SVG、MathML。 */
export function sanitizeMarkdown(html: string): string {
  return markdownPurifier.sanitize(html, {
    ADD_ATTR: ['language'],
    FORBID_TAGS: ['iframe', 'object', 'embed', 'script', 'style', 'link', 'meta', 'base', 'form'],
    FORBID_ATTR: ['autoplay', 'srcdoc'],
  })
}
