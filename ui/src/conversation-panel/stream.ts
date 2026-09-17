export class ConversationStream {
  private response: any
  private onNext: (chunk: any) => void
  private onComplete: (e?: any) => void
  private cancelled = false
  private completed = false
  private reader: ReadableStreamDefaultReader<any> | null = null

  constructor(
    response: any,
    onNext: (chunk: any) => void,
    onComplete: (e?: any) => void,
  ) {
    this.response = response
    this.onComplete = onComplete
    this.onNext = onNext
  }

  private complete(e?:any) {
    if (this.completed || this.cancelled) return
    this.completed = true
    this.onComplete(e)
  }

  async start() {
    try {
      this.reader = this.response.body?.getReader()
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
              const chunk = JSON.parse(data)
              this.onNext(chunk)
            } catch (e) {
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
              const chunk = JSON.parse(data)
              this.onNext(chunk)
            } catch (e) {
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
