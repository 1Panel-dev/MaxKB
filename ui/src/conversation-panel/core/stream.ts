import type { StreamChunk } from './types'

// SSE 流解析:逐段 data: {...} 回调 onNext，遇 [DONE]/结束/异常回调 onComplete(e?)。
export class ConversationStream<Chunk = StreamChunk> {
  private response: Response
  private onNext: (chunk: unknown) => void
  private onComplete: (e?: unknown) => void
  private cancelled = false
  private completed = false
  private reader: ReadableStreamDefaultReader<Uint8Array> | null = null

  constructor(response: Response, onNext: (chunk: Chunk) => void, onComplete: (e?: unknown) => void) {
    this.response = response
    this.onComplete = onComplete
    // JSON 在解析边界是 unknown，由调用方的分片协议约束回调类型。
    this.onNext = (chunk) => onNext(chunk as Chunk)
  }

  private complete(e?: unknown) {
    if (this.completed || this.cancelled) return
    this.completed = true
    this.onComplete(e)
  }

  async start() {
    try {
      this.reader = this.response.body?.getReader() ?? null
      if (!this.reader) {
        this.complete()
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        if (this.cancelled || this.completed) break

        const { done, value } = await this.reader.read()

        if (done) break

        const decoded = decoder.decode(value, { stream: true })
        buffer += decoded

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (this.cancelled || this.completed) break
          const trimmed = line.trim()
          if (!trimmed) continue

          // SSE 格式：data: {...}
          if (trimmed.startsWith('data:')) {
            const data = trimmed.slice(5).trim()
            if (data === '[DONE]') {
              this.complete()
              return
            }

            try {
              const chunk: unknown = JSON.parse(data)
              this.onNext(chunk)
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }

      // 处理 buffer 中剩余的数据
      if (!this.cancelled && !this.completed && buffer.trim()) {
        const trimmed = buffer.trim()
        if (trimmed.startsWith('data:')) {
          const data = trimmed.slice(5).trim()
          if (data !== '[DONE]') {
            try {
              const chunk: unknown = JSON.parse(data)
              this.onNext(chunk)
            } catch {
              // Skip invalid JSON
            }
          }
        }
      }

      if (!this.cancelled) {
        this.complete()
      }
    } catch (e) {
      if (!this.cancelled && !this.completed) {
        this.complete(e)
      }
    } finally {
      this.reader = null
    }
  }

  cancel() {
    this.cancelled = true
    // 关闭 reader 来中断读取
    if (this.reader) {
      this.reader.cancel().catch(() => {})
      this.reader = null
    }
  }
}
