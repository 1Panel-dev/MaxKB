<script setup lang="ts">
import type ChatLogApi from '@/api/admin/workspace/application/chat-log'
import ButtonImprove from './improve/ButtonImprove.vue'
import LogMessageFeedback from './feedback/index.vue'
import FeedbackCard from './feedback/FeedbackCard.vue'
import { computed } from 'vue'
import type { ChatContent } from '@/api/types'
import { copyText } from '@/utils/clipboard'
import { datetimeFormat } from '@/utils/time'
import type { ChatMessage, ChatRecordMeta } from '../../core/types'
import { useExecutionDetailStore } from '../../right-sidebar/execution-detail/index'

const props = defineProps<{
  api: Pick<typeof ChatLogApi, 'putChatRecordLog' | 'getMarkChatRecord' | 'deleteMarkChatRecord'>
  applicationId: string
  chatId: string
  message: ChatMessage
}>()

const detail = useExecutionDetailStore()

const EMPTY: ChatRecordMeta = {
  messageTokens: 0,
  answerTokens: 0,
  runTime: 0,
  knowledgeCount: 0,
  executionDetails: [],
}
const meta = computed<ChatRecordMeta>(() => props.message.record || EMPTY)
const tokens = computed(() => meta.value.messageTokens + meta.value.answerTokens)

// 仅复制回答正文，按展示顺序收集分组内的文本，不包含思考与工具参数。
function collectAnswerText(contents: ChatContent[]): string {
  return [...contents]
    .sort((left, right) => (left.id || '').localeCompare(right.id || ''))
    .flatMap((content) => {
      if (content.type === 'GROUP') return collectAnswerText(content.children ?? [])
      return content.type === 'TEXT' ? content.content || '' : []
    })
    .filter(Boolean)
    .join('\n\n')
}
const answerText = computed(() => collectAnswerText(props.message.content))

const openExecutionDetail = () => {
  detail.showExecutionDetail(meta.value.executionDetails || [])
}
</script>

<style scoped lang="scss"></style>

<template>
  <div class="mk-conversation-message-footer space-y-2">
    <!-- 助手消息底部信息栏:知识来源 / 执行详情 / Tokens · 耗时  -->
    <div class="flex-align-center gap-1">
      <el-button v-if="meta.knowledgeCount" text class="-ml-1">
        <MkIcon name="icon_reference_outlined" />
        <span>知识来源 ({{ meta.knowledgeCount }})</span>
      </el-button>

      <!-- 执行详情:对话结束时已拉取并缓存,点击直接在右侧展示 -->
      <el-button text @click="openExecutionDetail" class="-ml-1">
        <MkIcon name="icon_logs_outlined" />
        <span>执行详情</span>
      </el-button>
      <template v-if="meta.runTime || tokens">
        <el-divider direction="vertical" class="ml-2! mr-3!" />
        <span class="text-N600">Tokens {{ tokens }} · 耗时 {{ meta.runTime.toFixed(2) }}s</span>
      </template>
    </div>
    <!-- 其他操作 -->
    <div class="flex-align-center gap-2">
      <!-- 复制回答正文 -->
      <MkTooltip content="复制">
        <el-button text class="-ml-1" :disabled="!answerText" @click="copyText(answerText)">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </MkTooltip>
      <!-- 修正当前回答并保存到知识库 -->
      <span>
        <ButtonImprove
          v-if="message.recordId"
          :api="api"
          :application-id="applicationId"
          :chat-id="chatId"
          :record-id="message.recordId"
          :answer="answerText"
        />
      </span>
      <!-- 反馈 -->
      <LogMessageFeedback :status="meta.feedback?.vote_status" />
      <!-- 时间 -->
      <span v-if="meta.createTime" class="text-N600 ml-1">{{ datetimeFormat(meta.createTime) }}</span>
    </div>
    <FeedbackCard v-if="meta.feedback && (meta.feedback.vote_status === '0' || meta.feedback.vote_status === '1')" :feedback="meta.feedback" />
  </div>
</template>
