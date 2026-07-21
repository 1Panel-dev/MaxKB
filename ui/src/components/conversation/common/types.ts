export interface Conversation {
  id: string
  name: string
  createTime?: string
  updateTime?: string
}

export interface ChatMessage {
  role: 'USER' | 'ASSISTANT'
  content: any[]
  id: string
  write_ed?: boolean
}

export interface StreamChunk {
  content?: any[]
  chat_id?: string
  chat_record_id?: string
  [key: string]: any
}

export type ChatType = 'CHAT' | 'DEBUG'
