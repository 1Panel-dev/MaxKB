type Handler = (...args: any[]) => void

class ChatBus {
  private events = new Map<string, Set<Handler>>()

  on(event: string, handler: Handler) {
    if (!this.events.has(event)) {
      this.events.set(event, new Set())
    }
    this.events.get(event)!.add(handler)
    return () => this.off(event, handler)
  }

  off(event: string, handler: Handler) {
    this.events.get(event)?.delete(handler)
  }

  emit(event: string, ...args: any[]) {
    this.events.get(event)?.forEach((handler) => handler(...args))
  }

  clear() {
    this.events.clear()
  }
}

export const chatBus = new ChatBus()

export const ChatEvents = {
  OPEN_CONVERSATION: 'open:conversation',
  NEW_CONVERSATION: 'new:conversation',
  DELETE_CONVERSATION: 'delete:conversation',
  RENAME_CONVERSATION: 'rename:conversation',
  SEND_MESSAGE: 'send:message',
  STOP_GENERATING: 'stop:generating',
  REFRESH_LIST: 'refresh:list',
} as const
