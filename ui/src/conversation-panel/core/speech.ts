import type { StreamChunk } from './types'
import type { ChatContent } from '@/api/types'
import { MsgError } from '@/utils/message'

/** 模型语音合成：返回音频，失败时抛出带后端提示信息的错误。 */
export type TextToSpeech = (text: string) => Promise<Blob>

/** 朗读状态：播放中、暂停（保留进度）、已结束（播完、出错或停止）。 */
export type SpeechState = 'playing' | 'paused' | 'ended'

// 句末标点或换行处断句；英文句点需后跟空白，避免把小数、版本号切开。
const SENTENCE_BREAK = /[。！？!?；;…\n]+|\.\s+/g
// 首句尽快开读，后续合并为较长片段，减少模型语音请求次数与句间停顿。
const FIRST_SEGMENT_MIN_LENGTH = 8
const SEGMENT_MIN_LENGTH = 40

const browserSpeechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window

/** 模型语音始终可用；浏览器语音取决于浏览器是否支持 speechSynthesis。 */
export const isSpeechSupported = (textToSpeech?: TextToSpeech) => Boolean(textToSpeech) || browserSpeechSupported

/** Markdown 片段转为朗读文本：去掉代码块、图片、HTML 与格式符号，只保留可读文字。 */
function toSpeechText(markdown: string): string {
  return markdown
    .replace(/```[\s\S]*?```/g, '')
    .replace(/<(video|audio|script|style)[^>]*>[\s\S]*?<\/\1>/gi, '')
    .replace(/<[^>]+>/g, '')
    .replace(/!\[[^\]]*\]\([^)]*\)/g, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/^\s{0,3}(#{1,6}|>+|[-*+]|\d+\.)\s+/gm, '')
    .replace(/^\s*\|?\s*:?-{3,}.*$/gm, '')
    .replace(/\|/g, ' ')
    .replace(/(\*\*|__|~~)(.*?)\1/g, '$2')
    .replace(/`([^`]*)`/g, '$1')
    .replace(/[ \t]+/g, ' ')
    .replace(/\n{2,}/g, '\n')
    .trim()
}

/** 分片中的正文增量（含分组内），不包含思考、工具等内容。 */
function collectTextDeltas(contents: ChatContent[]): ChatContent[] {
  return contents.flatMap((content) => {
    if (content.type === 'GROUP') return collectTextDeltas(content.children ?? [])
    return content.type === 'TEXT' && content.content ? [content] : []
  })
}

/** 页面外部取消了浏览器语音队列。 */
class SpeechInterruptedError extends Error {}

/**
 * 一条回答的朗读：正文增量按内容项分别缓冲，凑满一句即入队；回答结束（finish）后读完剩余内容。
 * - 模型语音：逐段请求音频，只预取下一段；暂停即暂停 Audio，继续时从原位置播放。合成失败重试一次。
 * - 浏览器语音：逐段调用 speechSynthesis；暂停时取消当前句，继续时从该句开头重读。
 * 暂停期间仍接收增量并断句入队，只是不播放。
 */
export class StreamSpeech {
  private textToSpeech: TextToSpeech | undefined
  private onStateChange: ((state: SpeechState) => void) | undefined
  private state: SpeechState = 'playing'
  private buffers = new Map<string, string>()
  private segments: string[] = []
  private playIndex = 0
  private finished = false
  // 播放循环是否在处理某一段（合成中、播放中或模型语音暂停中）
  private running = false
  private audio?: HTMLAudioElement
  // 当前段音频已就绪且挂在 Audio 上，继续播放时直接 play
  private audioReady = false
  private audioRequests = new Map<number, Promise<string>>()
  private interruptCurrent?: () => void

  /** 未提供 textToSpeech 时使用浏览器语音；onStateChange 在暂停、继续、结束时调用。 */
  constructor(textToSpeech?: TextToSpeech, onStateChange?: (state: SpeechState) => void) {
    this.textToSpeech = textToSpeech
    this.onStateChange = onStateChange
  }

  /** 累积一个流式分片中的正文增量。 */
  appendChunk(chunk: StreamChunk) {
    if (this.state === 'ended' || !chunk) return
    const contents = Array.isArray(chunk.content) ? chunk.content : chunk.type ? [chunk] : []
    collectTextDeltas(contents).forEach((content) => this.appendText(content.id ?? '', content.content ?? ''))
  }

  /** 累积内容项 id 的正文增量；只在代码块围栏闭合处断句，避免读出未完成的代码。 */
  appendText(id: string, delta: string) {
    if (this.state === 'ended') return
    const text = (this.buffers.get(id) ?? '') + delta
    let cut = 0
    for (const match of text.matchAll(SENTENCE_BREAK)) {
      const end = match.index + match[0].length
      if (end - cut < (this.segments.length ? SEGMENT_MIN_LENGTH : FIRST_SEGMENT_MIN_LENGTH)) continue
      if ((text.slice(0, end).match(/```/g)?.length ?? 0) % 2) continue
      this.enqueue(text.slice(cut, end))
      cut = end
    }
    this.buffers.set(id, text.slice(cut))
  }

  /** 不再追加内容：剩余缓冲作为最后一段，播完后结束。 */
  finish() {
    if (this.state === 'ended') return
    this.buffers.forEach((text) => this.enqueue(text))
    this.buffers.clear()
    this.finished = true
    void this.run()
  }

  pause() {
    if (this.state !== 'playing') return
    this.setState('paused')
    if (this.textToSpeech) {
      this.audio?.pause()
    } else if (this.running) {
      window.speechSynthesis.cancel()
      this.interruptCurrent?.()
    }
  }

  resume() {
    if (this.state !== 'paused') return
    this.setState('playing')
    if (this.textToSpeech && this.audioReady) this.audio?.play().catch((error) => this.fail(error))
    void this.run()
  }

  stop() {
    if (this.state === 'ended') return
    const speaking = this.running && !this.textToSpeech
    this.setState('ended')
    // 仅在本次朗读播放中时清空浏览器语音队列
    if (speaking) window.speechSynthesis.cancel()
    this.audio?.pause()
    this.interruptCurrent?.()
    this.buffers.clear()
    this.audioRequests.forEach((request) => request.then((url) => URL.revokeObjectURL(url)).catch(() => {}))
    this.audioRequests.clear()
  }

  private setState(state: SpeechState) {
    this.state = state
    this.onStateChange?.(state)
  }

  private enqueue(segment: string) {
    const text = toSpeechText(segment)
    if (!text) return
    this.segments.push(text)
    // 刚入队的可能正是下一段，播放中不会经过播放循环，需在此预取
    this.prefetchAudio()
    void this.run()
  }

  /** 模型语音：只合成当前段与下一段，已请求的复用缓存。 */
  private prefetchAudio() {
    if (!this.textToSpeech || this.state === 'ended') return
    const end = Math.min(this.segments.length, this.playIndex + 2)
    for (let index = this.playIndex; index < end; index++) void this.requestAudio(index)
  }

  private requestAudio(index: number) {
    let request = this.audioRequests.get(index)
    const synthesize = this.textToSpeech
    if (!request && synthesize) {
      const text = this.segments[index] ?? ''
      // 合成失败重试一次
      request = synthesize(text)
        .catch(() => synthesize(text))
        .then((blob) => URL.createObjectURL(blob))
      // 预取失败在轮到该段时再抛出
      request.catch(() => {})
      this.audioRequests.set(index, request)
    }
    return request ?? Promise.reject(new Error('语音合成失败'))
  }

  private async run() {
    if (this.running || this.state !== 'playing') return
    this.running = true
    try {
      while (this.state === 'playing' && this.playIndex < this.segments.length) {
        const completed = this.textToSpeech ? await this.playAudio(this.playIndex) : await this.speak(this.segments[this.playIndex] ?? '')
        // 浏览器语音被暂停时当前句未读完，继续时重读
        if (!completed) break
        this.playIndex++
      }
    } catch (error) {
      this.running = false
      this.fail(error)
    } finally {
      this.running = false
    }
    if (this.state === 'playing' && this.finished && this.playIndex >= this.segments.length) this.stop()
  }

  // 外部打断或浏览器拦截自动播放时静默结束；其他失败提示一次并结束
  private fail(error: unknown) {
    if (this.state === 'ended') return
    const silent = error instanceof SpeechInterruptedError || (error instanceof DOMException && error.name === 'NotAllowedError')
    if (!silent) MsgError(error instanceof Error && error.message ? error.message : '语音播放失败')
    this.stop()
  }

  /** 浏览器语音读一句，读完返回 true；被暂停或停止返回 false。 */
  private speak(text: string) {
    return new Promise<boolean>((resolve, reject) => {
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.onend = () => resolve(true)
      utterance.onerror = (event) => {
        if (this.state !== 'playing') resolve(false)
        else if (event.error === 'interrupted' || event.error === 'canceled') reject(new SpeechInterruptedError())
        else resolve(true)
      }
      this.interruptCurrent = () => resolve(false)
      window.speechSynthesis.speak(utterance)
    })
  }

  /** 模型语音播放一段：暂停时保持等待，继续后从原位置播完；播完返回 true，停止返回 false。 */
  private async playAudio(index: number) {
    this.prefetchAudio()
    const url = await this.requestAudio(index)
    if (this.state === 'ended') return false
    const audio = (this.audio ??= new Audio())
    try {
      return await new Promise<boolean>((resolve, reject) => {
        audio.onended = () => resolve(true)
        audio.onerror = () => reject(new Error('语音播放失败'))
        this.interruptCurrent = () => resolve(false)
        audio.src = url
        this.audioReady = true
        if (this.state === 'playing') audio.play().catch(reject)
      })
    } finally {
      this.audioReady = false
      URL.revokeObjectURL(url)
    }
  }
}
