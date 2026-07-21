import { useChatStore } from './chat'
import { useDebugStore } from './debug'

export function useChatStoreByType(type: 'CHAT' | 'DEBUG', applicationId?: string) {
  return type === 'DEBUG' ? useDebugStore(applicationId) : useChatStore()
}
