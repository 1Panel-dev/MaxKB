export class ConversationStream {
  private response: any
  private onChunk: (chunk: any) => void
  private onFinish: () => void
  private onError: (e: any) => void
  private cancelled = false
  private finished = false
  private reader: ReadableStreamDefaultReader<any> | null = null

  constructor(
    response: any,
    onChunk: (chunk: any) => void,
    onFinish: () => void,
    onError: (e: any) => void,
  ) {
    this.response = response
    this.onChunk = onChunk
    this.onFinish = onFinish
    this.onError = onError
  }

  private finish() {
    if (this.finished || this.cancelled) return
    this.finished = true
    this.onFinish()
  }

  async start() {
    try {
      this.reader = this.response.body?.getReader()
      if (!this.reader) {
        this.finish()
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        if (this.cancelled || this.finished) break

        const { done, value } = await this.reader.read()

        if (done) break

        const decoded = decoder.decode(value, { stream: true })
        buffer += decoded

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (this.cancelled || this.finished) break
          const trimmed = line.trim()
          if (!trimmed) continue

          // SSE 格式：data: {...}
          if (trimmed.startsWith('data:')) {
            const data = trimmed.slice(5).trim()
            if (data === '[DONE]') {
              this.finish()
              return
            }

            try {
              const chunk = JSON.parse(data)
              this.onChunk(chunk)
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }

      // 处理 buffer 中剩余的数据
      if (!this.cancelled && !this.finished && buffer.trim()) {
        const trimmed = buffer.trim()
        if (trimmed.startsWith('data:')) {
          const data = trimmed.slice(5).trim()
          if (data !== '[DONE]') {
            try {
              const chunk = JSON.parse(data)
              this.onChunk(chunk)
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }

      if (!this.cancelled) {
        this.finish()
      }
    } catch (e) {
      if (!this.cancelled && !this.finished) {
        this.onError(e)
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
