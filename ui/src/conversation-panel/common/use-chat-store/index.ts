import { CHAT_TYPE } from '@/conversation-panel/common/enums'
import { useChatStore } from './chat'
import { useDebugStore } from './debug'
import type { ChatType } from '../types'

export function useChatStoreByType(type: ChatType) {
  return type === CHAT_TYPE.DEBUG ? useDebugStore() : useChatStore()
}
