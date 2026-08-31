import type { ChatMessage } from '../../types'
import { ConversationStream } from '../../../stream'
import { chatApi, debugApi } from '../../../api'

export interface StartStreamOptions {
  cid: string
  request: () => Promise<any>
  onStream: (chunk: any) => void
  onFinish?: () => void
  onFailure?: (e: any) => void
}

export interface SwitchOptions {
  cid: string
  loadMessages: (cid: string) => Promise<void>
  resumeStream: (chatRecordId: string) => Promise<Response>
  getLastMessage: () => ChatMessage | null
  onStream: (chunk: any) => void
  onFinish?: () => void
  onFailure?: () => void
  skipLoadMessages?: boolean
}

export function useStreamManager() {
  let currentStream: ConversationStream | null = null

  // 返回值表示本次是否真的关闭了一个进行中的流，供调用方判断是否需要通知后端取消
  const closeStream = () => {
    if (currentStream) {
      currentStream.cancel()
      currentStream = null
      return true
    }
    return false
    // 不在这里增加 streamToken，由调用方决定
  }

  const startStream = ({ cid, request, onStream, onFinish, onFailure }: StartStreamOptions) => {
    closeStream()

    request()
      .then((response: any) => {
        currentStream = new ConversationStream(
          response,
          onStream,
          () => {
            currentStream = null
            onFinish?.()
          },
          (e) => {
            currentStream = null
            onFailure?.(e)
          },
        )
        currentStream.start()
      })
      .catch((e: any) => {
        onFailure?.(e)
      })
  }

  const switchConversation = async (opts: SwitchOptions) => {
    const {
      cid,
      loadMessages,
      resumeStream,
      getLastMessage,
      onStream,
      onFinish,
      onFailure,
      skipLoadMessages,
    } = opts

    // 先关闭旧流
    closeStream()
    if (!skipLoadMessages) {
      await loadMessages(cid)
    }

    const lastMsg = getLastMessage()
    // 没有需要续传的流（无消息或最后一条消息已完成）时，同样要结束 loading 契约。
    if (!lastMsg || (lastMsg.content && lastMsg.content.length > 0)) {
      onFinish?.()
      return
    }
    try {
      const response = await resumeStream(lastMsg.id.replace('_USER', '').replace('_ASSISTANT', ''))
      if (!response.ok) {
        onFailure?.()
        return
      }
      currentStream = new ConversationStream(
        response,
        onStream,
        () => {
          currentStream = null
          onFinish?.()
        },
        () => {
          currentStream = null
          onFailure?.()
        },
      )
      currentStream.start()
    } catch (e) {
      console.error('resume stream failed', e)
      onFailure?.()
    }
  }

  // 优雅停止：仅通知后端取消，本地 SSE 不断开，继续读取。
  // 后端收到取消后会触发 on_complete 往队列放入 "done" 并 yield [DONE]，
  // 前端读到 [DONE] 由 ConversationStream 自行 finish（loading 交给 onFinish 复位）。
  // 若此刻就 abort 本地流，服务端 generator 不再被消费，[DONE] 那段永远跑不到。
  const stopWorkflow = (cid: string, apiType: 'chat' | 'debug' = 'chat', applicationId?: string) => {
    if (!currentStream || !cid) return
    const api = apiType === 'debug' ? debugApi : chatApi
    api.cancelChat(cid, applicationId).catch(() => {})
  }

  const cancelWorkflow = (cid: string, apiType: 'chat' | 'debug' = 'chat', applicationId?: string) => {
    // 硬取消：用于卸载/离开页面，必须断开本地流避免后台泄漏，同时通知后端。
    const wasStreaming = closeStream()
    // 仅当确实中断了一个进行中的流、且已有会话 id 时才通知后端取消。
    // debug 的 chat_id 是前端本地草稿，首发消息前服务端并不存在该会话，
    // 此时调用 cancel_chat_message 只会命中不存在的 chat_id，必须跳过。
    if (!wasStreaming || !cid) return
    const api = apiType === 'debug' ? debugApi : chatApi
    api.cancelChat(cid, applicationId).catch(() => {})
  }

  return {
    closeStream,
    startStream,
    switchConversation,
    stopWorkflow,
    cancelWorkflow,
  }
}
