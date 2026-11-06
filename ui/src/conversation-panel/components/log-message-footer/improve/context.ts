import type { InjectionKey, ComputedRef } from 'vue'
import type ChatLogApi from '@/api/admin/workspace/application/chat-log'

export const LOG_IMPROVE_KEY: InjectionKey<
  ComputedRef<{
    api: Pick<typeof ChatLogApi, 'putChatRecordLog' | 'getMarkChatRecord' | 'deleteMarkChatRecord'>
    applicationId: string
    chatId: string
  }>
> = Symbol('log-improve')
