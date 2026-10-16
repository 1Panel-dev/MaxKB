/** 消息与召回输入共用的附件入口和提交快捷键。 */
import { ref, type Ref } from 'vue'
import { inputShortcut } from './shortcuts'

/** 统一选择、拖拽、粘贴和回车行为，文件校验与提交条件由调用方维护。 */
export function useInputEvents(options: {
  text: Ref<string>
  canUpload: () => boolean
  addFiles: (files: FileList | File[]) => void
  submit: () => void
}) {
  const fileInputRef = ref<HTMLInputElement | null>(null)

  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement
    if (input.files && options.canUpload()) options.addFiles(input.files)
    input.value = ''
  }

  function handlePaste(event: ClipboardEvent) {
    const clipboard = event.clipboardData
    if (!clipboard?.files.length) return
    // 混合内容保留原生文本粘贴，附件单独上传。
    if (!clipboard.getData('text/plain')) event.preventDefault()
    if (options.canUpload()) options.addFiles(clipboard.files)
  }

  function handleDragover(event: DragEvent) {
    if (!event.dataTransfer?.types.includes('Files')) return
    event.preventDefault()
    event.dataTransfer.dropEffect = options.canUpload() ? 'copy' : 'none'
  }

  function handleDrop(event: DragEvent) {
    if (!event.dataTransfer?.files.length) return
    event.preventDefault()
    if (options.canUpload()) options.addFiles(event.dataTransfer.files)
  }

  function handleKeydown(event: KeyboardEvent) {
    const isMobile = /Mobi|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
    if (isMobile && event.key === 'Enter') return
    inputShortcut(event, options.text, options.submit)
  }

  return { fileInputRef, handleFileSelect, handlePaste, handleDragover, handleDrop, handleKeydown }
}
