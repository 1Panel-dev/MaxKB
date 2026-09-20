import { ref, inject, type InjectionKey } from 'vue'

/**
 * debug 面板状态:显隐 + 放大。debug header 深嵌在会话主面板内,用注入而非 props 获取。
 * 由 view/debug 创建并 provide,同时把 open/close 暴露给外层(工作流页)通过 ref 调用。
 */
export function createDebugHeaderStore() {
  const visible = ref(false)
  const expanded = ref(false)

  const open = () => (visible.value = true)
  const close = () => {
    visible.value = false
    expanded.value = false
  }
  const toggleExpand = () => (expanded.value = !expanded.value)

  return { visible, expanded, open, close, toggleExpand }
}

export type DebugHeaderStore = ReturnType<typeof createDebugHeaderStore>

export const DEBUG_HEADER_KEY: InjectionKey<DebugHeaderStore> = Symbol('debug-header')

export function useDebugHeaderStore(): DebugHeaderStore {
  const store = inject(DEBUG_HEADER_KEY)
  if (!store) throw new Error('useDebugHeaderStore 必须在 debug view 内使用')
  return store
}
