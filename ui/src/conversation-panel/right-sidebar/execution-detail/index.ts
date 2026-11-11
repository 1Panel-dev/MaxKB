import { ref } from 'vue'
import type { ChatRecordMeta } from '../../core/types'

/**
 * 执行详情面板 store：当前展示的执行详情数据。
 * 由右侧栏 store 创建并组合，右侧开合与面板切换由右侧栏 store 维护。
 */
export function createExecutionDetailStore() {
  const executionDetails = ref<ChatRecordMeta['executionDetails']>([])

  const setExecutionDetails = (details: ChatRecordMeta['executionDetails']) => {
    executionDetails.value = details
  }

  return { executionDetails, setExecutionDetails }
}

export type ExecutionDetailStore = ReturnType<typeof createExecutionDetailStore>
