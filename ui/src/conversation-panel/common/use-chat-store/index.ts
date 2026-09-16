import { useChatStore } from './chat'
import { useDebugStore } from './debug'
import type { ChatType } from '../types'

export function useChatStoreByType(type: ChatType) {
  return type === 'DEBUG' ? useDebugStore() : useChatStore()
}
