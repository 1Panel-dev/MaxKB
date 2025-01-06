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
interface Chunk {
  real_node_id: string
  chat_id: string
  chat_record_id: string
  content: string
  node_id: string
  up_node_id: string
  is_end: boolean
  node_is_end: boolean
  node_type: string
  view_type: string
  runtime_node_id: string
  child_node: any
}
interface chatType {
  id: string
  problem_text: string
  answer_text: string
  buffer: Array<String>
  answer_text_list: Array<{
    content: string
    chat_record_id?: string
    runtime_node_id?: string
    child_node?: any
  }>
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
    audio_list: Array<any>
  }
}

interface Node {
  buffer: Array<string>
  node_id: string
  up_node_id: string
  node_type: string
  view_type: string
  index: number
  is_end: boolean
}
interface WriteNodeInfo {
  current_node: any
  answer_text_list_index: number
  current_up_node?: any
  divider_content?: Array<string>
}
export class ChatRecordManage {
  id?: any
  ms: number
  chat: chatType
  is_close?: boolean
  write_ed?: boolean
  is_stop?: boolean
  loading?: Ref<boolean>
  node_list: Array<any>
  write_node_info?: WriteNodeInfo
  constructor(chat: chatType, ms?: number, loading?: Ref<boolean>) {
    this.ms = ms ? ms : 10
    this.chat = chat
    this.loading = loading
    this.is_stop = false
    this.is_close = false
    this.write_ed = false
    this.node_list = []
  }
  append_answer(
    chunk_answer: string,
    index?: number,
    chat_record_id?: string,
    runtime_node_id?: string,
    child_node?: any
  ) {
    const set_index = index != undefined ? index : this.chat.answer_text_list.length - 1
    const content = this.chat.answer_text_list[set_index]
      ? this.chat.answer_text_list[set_index].content + chunk_answer
      : chunk_answer
    this.chat.answer_text_list[set_index] = {
      content: content,
      chat_record_id,
      runtime_node_id,
      child_node
    }

    this.chat.answer_text = this.chat.answer_text + chunk_answer
  }
  get_current_up_node(run_node: any) {
    const index = this.node_list.findIndex((item) => item == run_node)
    if (index > 0) {
      const n = this.node_list[index - 1]
      return n
    }
    return undefined
  }
  get_run_node() {
    if (
      this.write_node_info &&
      (this.write_node_info.current_node.buffer.length > 0 ||
        !this.write_node_info.current_node.is_end)
    ) {
      return this.write_node_info
    }
    const run_node = this.node_list.filter((item) => item.buffer.length > 0 || !item.is_end)[0]

    if (run_node) {
      const index = this.node_list.indexOf(run_node)
      let current_up_node = undefined
      if (index > 0) {
        current_up_node = this.get_current_up_node(run_node)
      }
      let answer_text_list_index = 0
      if (
        current_up_node == undefined ||
        run_node.view_type == 'single_view' ||
        current_up_node.view_type == 'single_view'
      ) {
        const none_index = this.findIndex(
          this.chat.answer_text_list,
          (item) => item.content == '',
          'index'
        )
        if (none_index > -1) {
          answer_text_list_index = none_index
        } else {
          answer_text_list_index = this.chat.answer_text_list.length
        }
      } else {
        const none_index = this.findIndex(
          this.chat.answer_text_list,
          (item) => item.content === '',
          'index'
        )
        if (none_index > -1) {
          answer_text_list_index = none_index
        } else {
          answer_text_list_index = this.chat.answer_text_list.length - 1
        }
      }

      this.write_node_info = {
        current_node: run_node,
        divider_content: ['\n\n'],
        current_up_node: current_up_node,
        answer_text_list_index: answer_text_list_index
      }
      return this.write_node_info
    }
    return undefined
  }
  findIndex<T>(array: Array<T>, find: (item: T) => boolean, type: 'last' | 'index') {
    let set_index = -1
    for (let index = 0; index < array.length; index++) {
      const element = array[index]
      if (find(element)) {
        set_index = index
        if (type == 'index') {
          break
        }
      }
    }
    return set_index
  }
  closeInterval() {
    this.chat.write_ed = true
    this.write_ed = true
    if (this.loading) {
      this.loading.value = false
    }
    if (this.id) {
      clearInterval(this.id)
    }
    const last_index = this.findIndex(
      this.chat.answer_text_list,
      (item) => item.content == '',
      'last'
    )
    if (last_index > 0) {
      this.chat.answer_text_list.splice(last_index, 1)
    }
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
      const node_info = this.get_run_node()
      if (node_info == undefined) {
        if (this.is_close) {
          this.closeInterval()
        }
        return
      }
      const { current_node, answer_text_list_index, divider_content } = node_info
      if (current_node.buffer.length > 20) {
        const context = current_node.is_end
          ? current_node.buffer.splice(0)
          : current_node.buffer.splice(
              0,
              current_node.is_end ? undefined : current_node.buffer.length - 20
            )
        this.append_answer(
          (divider_content ? divider_content.splice(0).join('') : '') + context.join(''),
          answer_text_list_index,
          current_node.chat_record_id,
          current_node.runtime_node_id,
          current_node.child_node
        )
      } else if (this.is_close) {
        while (true) {
          const node_info = this.get_run_node()

          if (node_info == undefined) {
            break
          }
          this.append_answer(
            (node_info.divider_content ? node_info.divider_content.splice(0).join('') : '') +
              node_info.current_node.buffer.splice(0).join(''),
            node_info.answer_text_list_index,
            node_info.current_node.chat_record_id,
            node_info.current_node.runtime_node_id,
            node_info.current_node.child_node
          )
          if (node_info.current_node.buffer.length == 0) {
            node_info.current_node.is_end = true
          }
        }
        this.closeInterval()
      } else {
        const s = current_node.buffer.shift()
        if (s !== undefined) {
          this.append_answer(
            (divider_content ? divider_content.splice(0).join('') : '') + s,
            answer_text_list_index,
            current_node.chat_record_id,
            current_node.runtime_node_id,
            current_node.child_node
          )
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
  appendChunk(chunk: Chunk) {
    let n = this.node_list.find((item) => item.real_node_id == chunk.real_node_id)
    if (n) {
      n.buffer.push(...chunk.content)
      n.content += chunk.content
    } else {
      n = {
        buffer: [...chunk.content],
        content: chunk.content,
        real_node_id: chunk.real_node_id,
        node_id: chunk.node_id,
        chat_record_id: chunk.chat_record_id,
        up_node_id: chunk.up_node_id,
        runtime_node_id: chunk.runtime_node_id,
        child_node: chunk.child_node,
        node_type: chunk.node_type,
        index: this.node_list.length,
        view_type: chunk.view_type,
        is_end: false
      }
      this.node_list.push(n)
    }
    if (chunk.node_is_end) {
      n['is_end'] = true
    }
  }
  append(answer_text_block: string) {
    let set_index = this.findIndex(
      this.chat.answer_text_list,
      (item) => item.content == '',
      'index'
    )
    this.chat.answer_text_list[set_index] = { content: answer_text_block }
  }
}

export class ChatManagement {
  static chatMessageContainer: Dict<ChatRecordManage> = {}

  static addChatRecord(chat: chatType, ms: number, loading?: Ref<boolean>) {
    this.chatMessageContainer[chat.id] = new ChatRecordManage(chat, ms, loading)
  }
  static appendChunk(chatRecordId: string, chunk: Chunk) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.appendChunk(chunk)
    }
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
