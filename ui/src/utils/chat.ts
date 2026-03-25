import { ChatManagement, type chatType } from '@/api/type/application'
/**
 * 获取一个递归函数,处理流式数据
 * @param chat    每一条对话记录
 * @param reader  流数据
 * @param stream  是否是流式数据
 */
export const getWrite = (chat: any, reader: any, stream: boolean) => {
  let tempResult = ''

  const write_stream = async () => {
    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          ChatManagement.close(chat.id)
          return
        }

        const decoder = new TextDecoder('utf-8')
        let str = decoder.decode(value, { stream: true })

        tempResult += str
        const split = tempResult.match(/data:.*?}\n\n/g)
        if (split) {
          str = split.join('')
          tempResult = tempResult.replace(str, '')

          // 批量处理所有 chunk
          for (const item of split) {
            const chunk = JSON.parse(item.replace('data:', ''))
            chat.chat_id = chunk.chat_id
            chat.record_id = chunk.chat_record_id

            if (!chunk.is_end) {
              ChatManagement.appendChunk(chat.id, chunk)
            }

            if (chunk.is_end) {
              return Promise.resolve()
            }
          }
        }
        // 如果没有匹配到完整chunk，继续读取下一块
      }
    } catch (e) {
      return Promise.reject(e)
    }
  }

  const write_json = async () => {
    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          const result_block = JSON.parse(tempResult)
          if (result_block.code === 500) {
            return Promise.reject(result_block.message)
          } else {
            if (result_block.content) {
              ChatManagement.append(chat.id, result_block.content)
            }
          }
          ChatManagement.close(chat.id)
          return
        }

        if (value) {
          const decoder = new TextDecoder('utf-8')
          tempResult += decoder.decode(value)
        }
      }
    } catch (e) {
      return Promise.reject(e)
    }
  }

  return stream ? write_stream : write_json
}
