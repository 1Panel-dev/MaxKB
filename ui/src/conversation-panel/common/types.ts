export interface Conversation {
  id: string
  abstract: string
  application_id?: string
  create_time?: string
  update_time?: string
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
