import bus from '@/bus/index'
class Scroll {
  /**
   * 是否吸底
   */
  bottomSuction: boolean
  /**
   * 是否是用户滚动
   */
  isProgrammaticScroll?: boolean
  /**
   * 元素
   */
  element: any
  constructor(element: any) {
    this.bottomSuction = true
    this.isProgrammaticScroll = false
    this.element = element
    this.initEventListener()
  }
  initEventListener() {
    this.element.addEventListener('scroll', () => {
      // 如果是程序滚动 那么就是吸底
      if (this.isProgrammaticScroll) {
        this.isProgrammaticScroll = undefined
      } else {
        if (this.element.scrollHeight - this.element.scrollTop <= this.element.clientHeight + 15) {
          // 如果用户滚动 那么判断滚动条到底部高度 判断是否吸底
          this.bottomSuction = true
          this.isProgrammaticScroll = true
        } else {
          this.isProgrammaticScroll = undefined
          // 不吸底
          this.bottomSuction = false
        }
      }
    })
  }
  scrollBottom() {
    // 如果吸底 就滚动到最下面
    if (this.bottomSuction) {
      this.element.scrollTop = this.element.scrollHeight
      // 程序滚动
      this.isProgrammaticScroll = true
    }
  }
  forceBottom() {
    this.bottomSuction = true
    this.isProgrammaticScroll = true
    this.element.scrollTop = this.element.scrollHeight
    // 子组件渲染可能比 nextTick 晚，用 rAF 兜底
    requestAnimationFrame(() => {
      this.element.scrollTop = this.element.scrollHeight
      this.isProgrammaticScroll = true
    })
  }
}
export { Scroll }

const TEXT = (prev: any = {}, chunk: any) => ({
  type: 'TEXT',
  id: chunk.id ?? prev.id,
  content: (prev.content || '') + (chunk.content || ''),
  extra: chunk.extra ?? prev.extra,
})

const REASONING = (prev: any = {}, chunk: any) => ({
  type: 'REASONING',
  id: chunk.id ?? prev.id,
  content: (prev.content || '') + (chunk.content || ''),
  status: chunk.status ?? prev.status,
  extra: chunk.extra ?? prev.extra,
})

const FAILURE = (prev: any = {}, chunk: any) => ({
  type: 'FAILURE',
  id: chunk.id ?? prev.id,
  content: (prev.content || '') + (chunk.content || ''),
  extra: chunk.extra ?? prev.extra,
})

const TOOL = (prev: any = {}, chunk: any) => ({
  type: 'TOOL',
  id: chunk.id ?? prev.id,
  content: (prev.content || '') + (chunk.content || ''),
  arguments: (prev.arguments || '') + (chunk.arguments || ''),
  result: (prev.result || '') + (chunk.result || ''),
  status: chunk.status ?? prev.status,
  extra: chunk.extra ?? prev.extra,
})

const FORM = (prev: any = {}, chunk: any) => ({
  type: 'FORM',
  id: chunk.id ?? prev.id,
  form_field_list: chunk.form_field_list ?? prev.form_field_list ?? [],
  form_content_format: chunk.form_content_format ?? prev.form_content_format ?? '',
  is_submit: chunk.is_submit ?? prev.is_submit ?? false,
  form_data: chunk.form_data ?? prev.form_data ?? {},
  status: chunk.status ?? prev.status,
  extra: chunk.extra ?? prev.extra,
})

export const aggregators: any = {
  TEXT,
  REASONING,
  FAILURE,
  TOOL,
  FORM,
}

class ConversationStream {
  response: any
  reader?: ReadableStreamDefaultReader<Uint8Array>
  onStream: (chunk: any) => void
  onFinish: () => void
  onFailure: (e: any) => void
  cancelled = false
  tempChunk = ''

  constructor(
    response: any,
    onStream: (chunk: any) => void,
    onFinish: () => void,
    onFailure: (e: any) => void,
  ) {
    this.response = response
    this.onStream = onStream
    this.onFinish = onFinish
    this.onFailure = onFailure
  }

  stream() {
    this.response
      .then((res: any) => {
        if (this.cancelled) return
        if (!res.ok) {
          if (res.status === 403) {
            bus.emit('auth:403')
          }
          this.onFailure(new Error(`HTTP ${res.status}`))
          return
        }
        this.reader = res.body?.getReader()
        if (!this.reader) {
          this.onFailure(new Error('No response body'))
          return
        }
        this.readLoop()
      })
      .catch((e: any) => {
        if (!this.cancelled) this.onFailure(e)
      })
  }

  private async readLoop() {
    const decoder = new TextDecoder('utf-8')
    try {
      while (!this.cancelled) {
        const { done, value } = await this.reader!.read()
        if (done) {
          this.onFinish()
          return
        }
        this.tempChunk += decoder.decode(value, { stream: true })
        const split = this.tempChunk.match(/data:.*}\n\n/g)
        if (!split) continue
        const matched = split.join('')
        this.tempChunk = this.tempChunk.replace(matched, '')
        for (const item of split) {
          this.onStream(JSON.parse(item.replace('data:', '')))
        }
      }
    } catch (e) {
      if (!this.cancelled) this.onFailure(e)
    }
  }

  cancel() {
    this.cancelled = true
    this.reader?.cancel().catch(() => {})
  }
}
export { ConversationStream }
