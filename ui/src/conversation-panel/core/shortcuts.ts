/** 对话模块的输入快捷键处理，供消息输入框和内容生成弹窗复用。 */
import { nextTick, type Ref } from 'vue'

/**
 * 普通回车调用提交方法，组合键回车替换选区为换行并恢复光标。
 * 输入法组合期间不拦截事件；换行遵循 textarea 的 maxlength。
 * 调用方负责提交条件及事件冒泡控制。
 */
export function inputShortcut(event: KeyboardEvent, inputValue: Ref<string>, submit: () => void) {
  if (event.isComposing || event.key !== 'Enter') return
  event.preventDefault()

  if (event.ctrlKey || event.shiftKey || event.altKey || event.metaKey) {
    const textarea = event.target
    if (!(textarea instanceof HTMLTextAreaElement)) return
    const startPos = textarea.selectionStart
    const endPos = textarea.selectionEnd
    const content = inputValue.value.slice(0, startPos) + '\n' + inputValue.value.slice(endPos)
    if (textarea.maxLength >= 0 && content.length > textarea.maxLength) return
    inputValue.value = content
    nextTick(() => textarea.setSelectionRange(startPos + 1, startPos + 1))
    return
  }

  submit()
}
