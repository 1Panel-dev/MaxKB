import { type Dict } from '@/api/type/common'
import { type Ref } from 'vue'
interface ApplicationFormType {
  name?: string
  desc?: string
  model_id?: string
  multiple_rounds_dialogue?: boolean
  prologue?: string
  dataset_id_list?: string[]
  dataset_setting?: any
  model_setting?: any
  problem_optimization?: boolean
  icon?: string | undefined
}
interface chatType {
  id: string
  problem_text: string
  answer_text: string
  buffer: Array<String>
  /**
   * 是否寫入結束
   */
  write_ed?: boolean
  /**
   * 是否暫停
   */
  is_stop?: boolean
  record_id: string
  vote_status: string
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
  write() {
    this.chat.is_stop = false
    this.is_stop = false
    if (this.loading) {
      this.loading.value = true
    }
    this.id = setInterval(() => {
      if (this.chat.buffer.length > 20) {
        this.chat.answer_text =
          this.chat.answer_text + this.chat.buffer.splice(0, this.chat.buffer.length - 20).join('')
      } else if (this.is_close) {
        this.chat.answer_text = this.chat.answer_text + this.chat.buffer.splice(0).join('')
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
          this.chat.answer_text = this.chat.answer_text + s
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
  /**
   * 持續從緩存區 寫出數據
   * @param chatRecordId 對話記錄id
   */
  static write(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.write()
    }
  }
  /**
   * 等待所有數據輸出完畢後 才會關閉流
   * @param chatRecordId 對話記錄id
   * @returns boolean
   */
  static close(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.close()
    }
  }
  /**
   * 停止輸出 立即關閉定時任務輸出
   * @param chatRecordId 對話記錄id
   * @returns boolean
   */
  static stop(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.stop()
    }
  }
  /**
   * 判斷是否輸出完成
   * @param chatRecordId 對話記錄id
   * @returns boolean
   */
  static isClose(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    return chatRecord ? chatRecord.is_close && chatRecord.write_ed : false
  }
  /**
   * 判斷是否停止輸出
   * @param chatRecordId 對話記錄id
   * @returns
   */
  static isStop(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    return chatRecord ? chatRecord.is_stop : false
  }
  /**
   * 清除無用數據 也就是被close掉的和stop的數據
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
