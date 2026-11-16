import type ChatLogApi from '@/api/admin/workspace/application/chat-log'
import type { ComputedRef, InjectionKey } from 'vue'

export const LOG_IMPROVE_KEY: InjectionKey<
  ComputedRef<{
    api: Pick<typeof ChatLogApi, 'putChatRecordLog' | 'getMarkChatRecord' | 'deleteMarkChatRecord'>
    applicationId: string
    chatId: string
  }>
> = Symbol('log-improve')
