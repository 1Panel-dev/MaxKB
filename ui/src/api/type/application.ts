import { type Ref } from 'vue'
interface ApplicationFormType {
  name?: string
  desc?: string
  model_id: string
  multiple_rounds_dialogue: boolean
  prologue?: string
  example?: string[]
  dataset_id_list: string[]
}
interface chatType {
  id: string
  problem_text: string
  answer_text: string
  buffer: Array<String>
}

export class ChatManage {
  id?: NodeJS.Timer
  ms: number
  chat: chatType
  is_close?: boolean
  loading?: Ref<boolean>
  constructor(chat: chatType, ms?: number, loading?: Ref<boolean>) {
    this.ms = ms ? ms : 10
    this.chat = chat
    this.loading = loading
  }
  write() {
    this.id = setInterval(() => {
      const s = this.chat.buffer.shift()
      if (s !== undefined) {
        this.chat.answer_text = this.chat.answer_text + s
      } else {
        if (this.is_close) {
          clearInterval(this.id)
          if (this.loading) {
            this.loading.value = false
          }
        }
      }
    }, this.ms)
  }
  close() {
    this.is_close = true
  }
  append(answer_text_block: string) {
    for (let index = 0; index < answer_text_block.length; index++) {
      this.chat.buffer.push(answer_text_block[index])
    }
  }
}
export type { ApplicationFormType, chatType }
