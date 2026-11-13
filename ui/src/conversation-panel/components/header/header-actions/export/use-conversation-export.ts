import { computed, ref } from 'vue'
import DOMPurify from 'dompurify'
import type { ChatContent } from '@/api/types'
import { useMessageListStore } from '../../../message-list/index'
import { useConversationListStore } from '../../../../left-sidebar/conversation-list/index'
import { MsgError } from '@/utils/message'

export function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  link.click()
  // 浏览器开始下载后释放地址。
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function contentToMarkdown(content: ChatContent): string {
  if (['REASONING', 'TOOL', 'GROUP_TOOL'].includes(content.type)) return ''
  if (content.children) return content.children.map(contentToMarkdown).filter(Boolean).join('\n\n')
  const text = content.content ?? ''
  if (content.type === 'HTML') return `\`\`\`html\n${text}\n\`\`\``
  if (content.type === 'ECHARTS') return `\`\`\`json\n${text}\n\`\`\``
  const attachments = ['image_list', 'document_list', 'audio_list', 'video_list', 'other_list'].flatMap((field) => {
    const files = content[field]
    if (!Array.isArray(files)) return []
    return files.flatMap((file: { name?: string; url?: string }) => {
      if (!file.url) return []
      const name = (file.name ?? '附件').replace(/[\[\]\\]/g, '\\$&')
      return `${field === 'image_list' ? '!' : ''}[${name}](<${file.url.replace(/[<>\r\n]/g, '')}>)`
    })
  })
  return [text, ...attachments].filter(Boolean).join('\n\n')
}

export function useConversationExport() {
  const messages = useMessageListStore()
  const conversations = useConversationListStore()
  const loading = ref(false)
  const disabled = computed(() => !messages.messages.value.length || messages.loading.value || messages.streamLoading.value || loading.value)
  const fileName = () =>
    (conversations.currentConversation.value?.abstract || conversations.currentChatId.value || '对话记录').replace(/[\\/:*?"<>|\u0000-\u001f]/g, '_')

  async function exportText(format: 'markdown' | 'html') {
    if (disabled.value) return
    loading.value = true
    const name = fileName()
    try {
      const markdown = messages.messages.value
        .map((message) => `## ${message.role === 'USER' ? '用户' : '助手'}\n\n${message.content.map(contentToMarkdown).filter(Boolean).join('\n\n')}`)
        .join('\n\n')
      if (format === 'markdown') {
        downloadBlob(new Blob([markdown], { type: 'text/markdown;charset=utf-8' }), `${name}.md`)
      } else {
        const { marked } = await import('marked')
        const body = DOMPurify.sanitize(await marked.parse(markdown), { FORBID_TAGS: ['style', 'script', 'iframe', 'form', 'input', 'button'] })
        const html = `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>对话记录</title><style>body{max-width:900px;margin:32px auto;padding:0 24px;font:16px/1.7 sans-serif;overflow-wrap:anywhere}img,video{max-width:100%}pre{white-space:pre-wrap;padding:16px;background:#f5f6f7}table{border-collapse:collapse}td,th{border:1px solid #ddd;padding:8px}</style></head><body>${body}</body></html>`
        downloadBlob(new Blob([html], { type: 'text/html;charset=utf-8' }), `${name}.html`)
      }
    } catch {
      MsgError('导出失败，请稍后重试')
    } finally {
      loading.value = false
    }
  }
  return { disabled, loading, fileName, exportText }
}
