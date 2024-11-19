import { type Dict } from '@/api/type/common'
import { type Ref } from 'vue'
interface ApplicationFormType {
  name?: string
  desc?: string
  model_id?: string
  dialogue_number?: number
  prologue?: string
  dataset_id_list?: string[]
  dataset_setting?: any
  model_setting?: any
  problem_optimization?: boolean
  problem_optimization_prompt?: string
  icon?: string | undefined
  type?: string
  work_flow?: any
  model_params_setting?: any
  tts_model_params_setting?: any
  stt_model_id?: string
  tts_model_id?: string
  stt_model_enable?: boolean
  tts_model_enable?: boolean
  tts_type?: string
}
interface chatType {
  id: string
  problem_text: string
  answer_text: string
  buffer: Array<String>
  answer_text_list: Array<string>
  /**
   * 是否写入结束
   */
  write_ed?: boolean
  /**
   * 是否暂停
   */
  is_stop?: boolean
  record_id: string
  chat_id: string
  vote_status: string
  status?: number
  execution_details: any[]
  upload_meta?: {
    document_list: Array<any>
    image_list: Array<any>
  }
}

export class ChatRecordManage {
  id?: any
  ms: number
  chat: chatType
  is_close?: boolean
  write_ed?: boolean
  is_stop?: boolean
  loading?: Ref<boolean>
  constructor(chat: chatType, ms?: number, loading?: Ref<boolean>) {
    this.ms = ms ? ms : 10
    this.chat = chat
    this.loading = loading
    this.is_stop = false
    this.is_close = false
    this.write_ed = false
  }
  append_answer(chunk_answer: String) {
    this.chat.answer_text_list[this.chat.answer_text_list.length - 1] =
      this.chat.answer_text_list[this.chat.answer_text_list.length - 1] + chunk_answer
    this.chat.answer_text = this.chat.answer_text + chunk_answer
  }
  write() {
    this.chat.is_stop = false
    this.is_stop = false
    this.is_close = false
    this.write_ed = false
    this.chat.write_ed = false
    if (this.loading) {
      this.loading.value = true
    }
    this.id = setInterval(() => {
      if (this.chat.buffer.length > 20) {
        this.append_answer(this.chat.buffer.splice(0, this.chat.buffer.length - 20).join(''))
      } else if (this.is_close) {
        this.append_answer(this.chat.buffer.splice(0).join(''))
        this.chat.write_ed = true
        this.write_ed = true
        if (this.loading) {
          this.loading.value = false
        }
        if (this.id) {
          clearInterval(this.id)
        }
      } else {
        const s = this.chat.buffer.shift()
        if (s !== undefined) {
          this.append_answer(s)
        }
      }
    }, this.ms)
  }
  stop() {
    clearInterval(this.id)
    this.is_stop = true
    this.chat.is_stop = true
    if (this.loading) {
      this.loading.value = false
    }
  }
  close() {
    this.is_close = true
  }
  open() {
    this.is_close = false
    this.is_stop = false
  }
  append(answer_text_block: string) {
    for (let index = 0; index < answer_text_block.length; index++) {
      this.chat.buffer.push(answer_text_block[index])
    }
  }
}

export class ChatManagement {
  static chatMessageContainer: Dict<ChatRecordManage> = {}

  static addChatRecord(chat: chatType, ms: number, loading?: Ref<boolean>) {
    this.chatMessageContainer[chat.id] = new ChatRecordManage(chat, ms, loading)
  }
  static append(chatRecordId: string, content: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.append(content)
    }
  }
  static updateStatus(chatRecordId: string, code: number) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.chat.status = code
    }
  }
  /**
   * 持续从缓存区 写出数据
   * @param chatRecordId 对话记录id
   */
  static write(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.write()
    }
  }
  /**
   * 等待所有数据输出完毕后 才会关闭流
   * @param chatRecordId 对话记录id
   * @returns boolean
   */
  static close(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.close()
    }
  }
  /**
   * 停止输出 立即关闭定时任务输出
   * @param chatRecordId 对话记录id
   * @returns boolean
   */
  static stop(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.stop()
    }
  }
  /**
   * 判断是否输出完成
   * @param chatRecordId 对话记录id
   * @returns boolean
   */
  static isClose(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    return chatRecord ? chatRecord.is_close && chatRecord.write_ed : false
  }
  /**
   * 判断是否停止输出
   * @param chatRecordId 对话记录id
   * @returns
   */
  static isStop(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    return chatRecord ? chatRecord.is_stop : false
  }
  /**
   * 清除无用数据 也就是被close掉的和stop的数据
   */
  static clean() {
    for (const key in Object.keys(this.chatMessageContainer)) {
      if (this.chatMessageContainer[key].is_close) {
        delete this.chatMessageContainer[key]
      }
    }
  }
}
export type { ApplicationFormType, chatType }
