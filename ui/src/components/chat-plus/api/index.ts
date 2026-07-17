import * as chat from './chat'
import * as debug from './debug'

export type ChatType = 'CHAT' | 'DEBUG'

const apis = { CHAT: chat, DEBUG: debug } as const

export const useApi = (type: ChatType) => apis[type]
