import { type Dict } from '@/api/type/common'
import { type Ref } from 'vue'
import bus from '@/bus'
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
  tts_autoplay?: boolean
  stt_autosend?: boolean
}
interface Chunk {
  real_node_id: string
  chat_id: string
  chat_record_id: string
  content: string
  reasoning_content: string
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
  answer_text_list: Array<
    Array<{
      content: string
      reasoning_content: string
      chat_record_id?: string
      runtime_node_id?: string
      child_node?: any
      real_node_id?: string
    }>
  >
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
    other_list: Array<any>
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
  divider_reasoning_content?: Array<string>
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
    reasoning_content: string,
    index?: number,
    chat_record_id?: string,
    runtime_node_id?: string,
    child_node?: any,
    real_node_id?: string
  ) {
    if (chunk_answer || reasoning_content) {
      const set_index = index != undefined ? index : this.chat.answer_text_list.length - 1
      let card_list = this.chat.answer_text_list[set_index]
      if (!card_list) {
        card_list = []
        this.chat.answer_text_list[set_index] = card_list
      }
      const answer_value = card_list.find((item) => item.real_node_id == real_node_id)
      const content = answer_value ? answer_value.content + chunk_answer : chunk_answer
      const _reasoning_content = answer_value
        ? answer_value.reasoning_content + reasoning_content
        : reasoning_content
      if (answer_value) {
        answer_value.content = content
        answer_value.reasoning_content = _reasoning_content
      } else {
        card_list.push({
          content: content,
          reasoning_content: _reasoning_content,
          chat_record_id,
          runtime_node_id,
          child_node,
          real_node_id
        })
      }
    }
    this.chat.answer_text = this.chat.answer_text + chunk_answer
    bus.emit('change:answer', { record_id: this.chat.record_id, is_end: false })
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
      (this.write_node_info.current_node.reasoning_content_buffer.length > 0 ||
        this.write_node_info.current_node.buffer.length > 0 ||
        !this.write_node_info.current_node.is_end)
    ) {
      return this.write_node_info
    }
    const run_node = this.node_list.filter(
      (item) => item.reasoning_content_buffer.length > 0 || item.buffer.length > 0 || !item.is_end
    )[0]

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
          (item) => (item.length == 1 && item[0].content == '') || item.length == 0,
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
          (item) => (item.length == 1 && item[0].content == '') || item.length == 0,
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
    bus.emit('change:answer', { record_id: this.chat.record_id, is_end: true })
    if (this.id) {
      clearInterval(this.id)
    }
    const last_index = this.findIndex(
      this.chat.answer_text_list,
      (item) => (item.length == 1 && item[0].content == '') || item.length == 0,
      'last'
    )
    if (last_index > 0) {
      this.chat.answer_text_list.splice(last_index, 1)
    }
  }
  write() {
    this.chat.is_stop = false
    this.is_stop = false
    if (!this.is_close) {
      this.is_close = false
    }

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
      const { current_node, answer_text_list_index } = node_info

      if (current_node.buffer.length > 20) {
        const context = current_node.is_end
          ? current_node.buffer.splice(0)
          : current_node.buffer.splice(
              0,
              current_node.is_end ? undefined : current_node.buffer.length - 20
            )
        const reasoning_content = current_node.is_end
          ? current_node.reasoning_content_buffer.splice(0)
          : current_node.reasoning_content_buffer.splice(
              0,
              current_node.is_end ? undefined : current_node.reasoning_content_buffer.length - 20
            )
        this.append_answer(
          context.join(''),
          reasoning_content.join(''),
          answer_text_list_index,
          current_node.chat_record_id,
          current_node.runtime_node_id,
          current_node.child_node,
          current_node.real_node_id
        )
      } else if (this.is_close) {
        while (true) {
          const node_info = this.get_run_node()

          if (node_info == undefined) {
            break
          }
          this.append_answer(
            node_info.current_node.buffer.splice(0).join(''),
            node_info.current_node.reasoning_content_buffer.splice(0).join(''),
            node_info.answer_text_list_index,
            node_info.current_node.chat_record_id,
            node_info.current_node.runtime_node_id,
            node_info.current_node.child_node,
            node_info.current_node.real_node_id
          )

          if (
            node_info.current_node.buffer.length == 0 &&
            node_info.current_node.reasoning_content_buffer.length == 0
          ) {
            node_info.current_node.is_end = true
          }
        }
        this.closeInterval()
      } else {
        const s = current_node.buffer.shift()
        const reasoning_content = current_node.reasoning_content_buffer.shift()
        if (s !== undefined) {
          this.append_answer(
            s,
            '',
            answer_text_list_index,
            current_node.chat_record_id,
            current_node.runtime_node_id,
            current_node.child_node,
            current_node.real_node_id
          )
        }
        if (reasoning_content !== undefined) {
          this.append_answer(
            '',
            reasoning_content,
            answer_text_list_index,
            current_node.chat_record_id,
            current_node.runtime_node_id,
            current_node.child_node,
            current_node.real_node_id
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
      if (chunk.reasoning_content) {
        n.reasoning_content_buffer.push(...chunk.reasoning_content)
        n.reasoning_content += chunk.reasoning_content
      }
    } else {
      n = {
        buffer: [...chunk.content],
        reasoning_content_buffer: chunk.reasoning_content ? [...chunk.reasoning_content] : [],
        reasoning_content: chunk.reasoning_content ? chunk.reasoning_content : '',
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
  append(answer_text_block: string, reasoning_content?: string) {
    let set_index = this.findIndex(
      this.chat.answer_text_list,
      (item) => item.length == 1 && item[0].content == '',
      'index'
    )
    if (set_index <= -1) {
      set_index = 0
    }
    this.chat.answer_text_list[set_index] = [
      {
        content: answer_text_block,
        reasoning_content: reasoning_content ? reasoning_content : ''
      }
    ]
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
  static append(chatRecordId: string, content: string, reasoning_content?: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.append(content, reasoning_content)
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
  static open(chatRecordId: string) {
    const chatRecord = this.chatMessageContainer[chatRecordId]
    if (chatRecord) {
      chatRecord.open()
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
