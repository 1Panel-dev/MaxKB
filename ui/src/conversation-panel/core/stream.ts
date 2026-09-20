// SSE 流解析:逐段 data: {...} 回调 onNext，遇 [DONE]/结束/异常回调 onComplete(e?)。
export class ConversationStream {
  private response: any
  private onNext: (chunk: any) => void
  private onComplete: (e?: any) => void
  private cancelled = false
  private completed = false
  private reader: ReadableStreamDefaultReader<any> | null = null

  constructor(response: any, onNext: (chunk: any) => void, onComplete: (e?: any) => void) {
    this.response = response
    this.onComplete = onComplete
    this.onNext = onNext
  }

  private complete(e?: any) {
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

// 消息容器“贴底吸附”滚动:用户上滑离底后不再自动吸底，回到底部附近恢复吸附。
export class Scroll {
  private bottomSuction: boolean
  private isProgrammaticScroll?: boolean
  private element: HTMLElement

  constructor(element: HTMLElement) {
    this.bottomSuction = true
    this.isProgrammaticScroll = false
    this.element = element
    this.initEventListener()
  }

  private initEventListener() {
    this.element.addEventListener('scroll', () => {
      if (this.isProgrammaticScroll) {
        this.isProgrammaticScroll = undefined
      } else {
        if (this.element.scrollHeight - this.element.scrollTop <= this.element.clientHeight + 15) {
          this.bottomSuction = true
          this.isProgrammaticScroll = true
        } else {
          this.isProgrammaticScroll = undefined
          this.bottomSuction = false
        }
      }
    })
  }

  scrollBottom() {
    if (this.bottomSuction) {
      this.element.scrollTop = this.element.scrollHeight
      this.isProgrammaticScroll = true
    }
  }

  forceBottom() {
    this.bottomSuction = true
    this.isProgrammaticScroll = true
    this.element.scrollTop = this.element.scrollHeight
    requestAnimationFrame(() => {
      this.element.scrollTop = this.element.scrollHeight
      this.isProgrammaticScroll = true
    })
  }
}
