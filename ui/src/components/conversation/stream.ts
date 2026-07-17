export class ConversationStream {
  private response: any
  private onChunk: (chunk: any) => void
  private onFinish: () => void
  private onError: (e: any) => void
  private cancelled = false
  private finished = false

  constructor(
    response: any,
    onChunk: (chunk: any) => void,
    onFinish: () => void,
    onError: (e: any) => void
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
      const reader = this.response.body?.getReader()
      if (!reader) {
        console.log('No reader available, calling onFinish')
        this.finish()
        return
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        if (this.cancelled || this.finished) break

        const { done, value } = await reader.read()
        if (done) break

        const decoded = decoder.decode(value, { stream: true })
        console.log('Raw decoded:', decoded)
        buffer += decoded
        
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (this.cancelled || this.finished) break
          const trimmed = line.trim()
          if (!trimmed) continue

          console.log('Processing line:', trimmed)

          // SSE 格式：data: {...}
          if (trimmed.startsWith('data:')) {
            const data = trimmed.slice(5).trim()
            if (data === '[DONE]') {
              console.log('Received [DONE], finishing stream')
              this.finish()
              return
            }

            try {
              const chunk = JSON.parse(data)
              console.log('Parsed SSE chunk:', chunk)
              this.onChunk(chunk)
            } catch (e) {
              console.warn('Failed to parse SSE data:', data, e)
            }
          } else {
            // 尝试直接解析为 JSON
            try {
              const chunk = JSON.parse(trimmed)
              if (chunk && typeof chunk === 'object') {
                console.log('Parsed JSON chunk:', chunk)
                this.onChunk(chunk)
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }

      // 处理 buffer 中剩余的数据
      if (!this.cancelled && !this.finished && buffer.trim()) {
        const trimmed = buffer.trim()
        console.log('Processing remaining buffer:', trimmed)
        
        if (trimmed.startsWith('data:')) {
          const data = trimmed.slice(5).trim()
          if (data !== '[DONE]') {
            try {
              const chunk = JSON.parse(data)
              console.log('Parsed remaining SSE chunk:', chunk)
              this.onChunk(chunk)
            } catch (e) {
              console.warn('Failed to parse remaining SSE data:', data, e)
            }
          }
        } else {
          try {
            const chunk = JSON.parse(trimmed)
            if (chunk && typeof chunk === 'object') {
              console.log('Parsed remaining JSON chunk:', chunk)
              this.onChunk(chunk)
            }
          } catch (e) {
            console.warn('Failed to parse remaining JSON:', trimmed, e)
          }
        }
      }

      if (!this.cancelled) {
        console.log('Stream finished, calling onFinish')
        this.finish()
      }
    } catch (e) {
      console.error('Stream error:', e)
      if (!this.cancelled && !this.finished) {
        this.onError(e)
      }
    }
  }

  cancel() {
    this.cancelled = true
  }
}
