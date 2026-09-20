import { ref, inject, type InjectionKey } from 'vue'

/**
 * execution-detail 组件 store:本组件独有——执行详情数据 + 右侧开合。
 * 消息内容项点击「执行详情」时,注入本 store 调 showExecutionDetail 打开右侧。
 */
export function createExecutionDetailStore() {
  const detail = ref<any[] | null>(null)
  const rightSideOpen = ref(false)

  const showExecutionDetail = (d: any[]) => {
    detail.value = d
    rightSideOpen.value = true
  }

  return {
    detail,
    rightSideOpen,
    showExecutionDetail,
    toggleRightSide: () => (rightSideOpen.value = !rightSideOpen.value),
    openRightSide: () => (rightSideOpen.value = true),
    closeRightSide: () => (rightSideOpen.value = false),
  }
}

export type ExecutionDetailStore = ReturnType<typeof createExecutionDetailStore>

export const EXECUTION_DETAIL_KEY: InjectionKey<ExecutionDetailStore> = Symbol('execution-detail')

export function useExecutionDetailStore(): ExecutionDetailStore {
  const store = inject(EXECUTION_DETAIL_KEY)
  if (!store) throw new Error('useExecutionDetailStore 必须在 ConversationView 内使用')
  return store
}
