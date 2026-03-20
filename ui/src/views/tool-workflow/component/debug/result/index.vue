<template>
  <el-tabs v-model="activeName" class="demo-tabs">
    <el-tab-pane label="输出" name="result">
      <div class="mt-8">
        <h4 class="title-decoration-1 mb-16 mt-16">回复内容</h4>

        <el-card
          style="height: 400px; overflow: auto"
          :class="isSuccess ? '' : 'color-danger'"
          class="pre-wrap"
          shadow="never"
        >
          <AnswerContent
            :application="details"
            :loading="loading"
            v-model:chat-record="currentChat"
            type="ai-chat"
            :send-message="sendMessage"
            :chat-management="ChatManagement"
            :executionIsRightPanel="false"
            @open-execution-detail="() => {}"
            @openParagraph="() => {}"
            @openParagraphDocument="() => {}"
            :selection="true"
          ></AnswerContent>
        </el-card>
      </div>
      <h4 class="title-decoration-1 mb-16 mt-16">输出参数</h4>
      <div class="mb-16" v-if="isSuccess !== undefined">
        <el-alert
          v-if="isSuccess"
          :title="$t('views.tool.form.debug.runSuccess')"
          type="success"
          show-icon
          :closable="false"
        />
        <el-alert
          v-else
          :title="$t('views.tool.form.debug.runFailed')"
          type="error"
          show-icon
          :closable="false"
        />
      </div>
      <el-card
        style="overflow: auto"
        :class="isSuccess ? '' : 'color-danger'"
        class="pre-wrap"
        shadow="never"
      >
        {{ output }}
      </el-card>
    </el-tab-pane>
    <el-tab-pane label="执行详情" name="executionDetails">
      <template v-for="(item, index) in arraySort(executionDetails ?? [], 'index')" :key="index">
        <ExecutionDetailCard :data="item"> </ExecutionDetailCard>
      </template>
    </el-tab-pane>
  </el-tabs>
</template>
<script setup lang="ts">
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import { ref, reactive, computed } from 'vue'
import { randomId } from '@/utils/common'
import { ChatManagement, type chatType } from '@/api/type/application'
import { t } from '@/locales'
import AnswerContent from '@/components/ai-chat/component/answer-content/index.vue'
import ExecutionDetailCard from '@/components/execution-detail-card/index.vue'
import { arraySort } from '@/utils/array'

const props = defineProps<{
  isShared: boolean
  apiType: 'systemShare' | 'workspace' | 'systemManage' | 'workspaceShare'
  toolDetails: any
}>()
const activeName = ref<string>('result')
const details = {
  show_avatar: false,
  show_user_avatar: false,
}
const currentToolId = ref<string>()
const currentData = ref<any>({})

const output = computed(() => {
  if (toolRecord.value) {
    return toolRecord.value.meta.output
  }
  return {}
})

const executionDetails = computed(() => {
  if (toolRecord.value) {
    return Object.values(toolRecord.value.meta.details)
  }
  return []
})

const showResult = ref<boolean>(false)

const isSuccess = computed(() => {
  if (toolRecord.value) {
    return toolRecord.value.state == 'FAILURE' ? false : true
  }
  return undefined
})

const toolRecord = ref<any>()

const execute = (toolId: string, data: any) => {
  currentToolId.value = toolId
  currentData.value = data
  ChatManagement.addChatRecord(currentChat, 50, loading)
  ChatManagement.write(currentChat.id)
  return loadSharedApi({ type: 'tool', isShared: props.isShared, systemType: props.apiType })
    .debugToolWorkflow(toolId, data)
    .then((response: any) => {
      if (response.status === 460) {
        return Promise.reject(t('chat.tip.errorIdentifyMessage'))
      } else if (response.status === 461) {
        return Promise.reject(t('chat.tip.errorLimitMessage'))
      } else {
        const reader = response.body.getReader()
        // 处理流数据
        const write = getWrite(
          currentChat,
          reader,
          response.headers.get('Content-Type') !== 'application/json',
        )
        return write()
      }
    })
    .finally(() => {
      getToolRecord()
      ChatManagement.close(currentChat.id)
    })
    .catch((e: any) => {
      console.log(e)
    })
}
const loading = ref<boolean>(false)
const currentChat = reactive<any>({
  id: randomId(),
  answer_text_list: [[]],
  buffer: [],
  reasoning_content: '',
  reasoning_content_buffer: [],
  write_ed: false,
  is_stop: false,
  record_id: '',
  chat_id: '',
  vote_status: '-1',
  status: undefined,
})
/**
 * 获取一个递归函数,处理流式数据
 * @param chat    每一条对话记录
 * @param reader  流数据
 * @param stream  是否是流式数据
 */
const getWrite = (chat: any, reader: any, stream: boolean) => {
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

const sendMessage = (val: string, other_params_data?: any, chat?: chatType) => {
  loadSharedApi({ type: 'tool', isShared: props.isShared, systemType: props.apiType })
    .debugToolWorkflow(currentToolId.value, { ...other_params_data, ...currentData.value })
    .then((response: any) => {
      if (response.status === 460) {
        return Promise.reject(t('chat.tip.errorIdentifyMessage'))
      } else if (response.status === 461) {
        return Promise.reject(t('chat.tip.errorLimitMessage'))
      } else {
        const reader = response.body.getReader()
        // 处理流数据
        const write = getWrite(
          currentChat,
          reader,
          response.headers.get('Content-Type') !== 'application/json',
        )
        return write()
      }
    })
    .finally(() => {
      ChatManagement.close(currentChat.id)
      getToolRecord()
    })
    .catch((e: any) => {
      console.log(e)
    })
  return Promise.resolve(true)
}
const getToolRecord = () => {
  loadSharedApi({
    type: 'tool',
    isShared: props.isShared,
    systemType: props.apiType,
  })
    .getToolRecordDetail(currentToolId.value, currentChat.record_id)
    .then((ok: any) => {
      toolRecord.value = ok.data
    })
}
defineExpose({
  execute,
})
</script>
<style lang="scss" scoped></style>
