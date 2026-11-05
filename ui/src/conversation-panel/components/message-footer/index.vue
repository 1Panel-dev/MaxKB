<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref } from 'vue'
import ButtonFeedback from './feedback/ButtonFeedback.vue'
import FeedbackCard from './feedback/FeedbackCard.vue'
import { MsgSuccess } from '@/utils/message'
import type { ChatContent, ChatFeedback } from '@/api/types'
import { copyText } from '@/utils/clipboard'
import { datetimeFormat } from '@/utils/time'
import type { ChatMessage, ChatRecordMeta } from '../../core/types'
import { useExecutionDetailStore } from '../../right-sidebar/execution-detail/index'

import { MESSAGE_LIST_KEY } from '../message-list/index'
import { SHAREABLE_VIEWS, useShareLinkStoreOptional } from '../message-list/share/index'
import { useViewType } from '../../view/index'

const props = defineProps<{ message: ChatMessage }>()
const emit = defineEmits<{ resize: [] }>()
const footerRef = ref<HTMLElement>()

// 反馈展开动画逐帧改变高度，由消息列表决定是否继续跟随底部。
let footerObserver: ResizeObserver | undefined
onMounted(() => {
  footerObserver = new ResizeObserver(() => emit('resize'))
  if (footerRef.value) footerObserver.observe(footerRef.value)
})
onBeforeUnmount(() => footerObserver?.disconnect())

// 仅提供分享服务的视图（对话、门户）显示分享入口；进入分享时预先勾选当前回答所属轮次。
const showShare = SHAREABLE_VIEWS.includes(useViewType())
const shareLink = useShareLinkStoreOptional()
// 回答生成中禁用分享。
const messageList = inject(MESSAGE_LIST_KEY, null)
const canShare = computed(() => Boolean(messageList?.messages.value.length && !messageList.streamLoading.value))

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
// 消息反馈：Footer 协调按钮、草稿面板与提交状态。
const canFeedback = computed(() => Boolean(messageList?.feedback && props.message.recordId && props.message.record))
const draftStatus = ref<'0' | '1'>()
const reason = ref<ChatFeedback['vote_reason']>(null)
const content = ref('')
const submitting = ref(false)
const currentStatus = computed(() => props.message.record?.feedback?.vote_status ?? '-1')

// 已提交反馈先撤销再重新评价，避免后端重复投票；请求失败保留草稿。
async function saveFeedback(data: ChatFeedback) {
  if (!messageList?.feedback || !props.message.recordId || submitting.value) return
  const message = props.message
  submitting.value = true
  try {
    await messageList.feedback(message.recordId!, data)
    if (message.record) message.record.feedback = data
    draftStatus.value = undefined
    MsgSuccess(data.vote_status === '-1' ? '已取消反馈' : '感谢你的反馈')
  } catch {
    // 请求层统一提示错误，保留当前填写内容供重试。
  } finally {
    submitting.value = false
  }
}

function openFeedback(status: '0' | '1') {
  if (currentStatus.value === status) {
    void saveFeedback({ vote_status: '-1' })
    return
  }
  draftStatus.value = draftStatus.value === status ? undefined : status
  reason.value = null
  content.value = ''
}
</script>

<style scoped lang="scss"></style>

<template>
  <div ref="footerRef" class="mk-conversation-message-footer space-y-2">
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
    <div class="flex-align-center flex-wrap gap-2">
      <!-- 复制回答正文 -->
      <MkTooltip content="复制">
        <el-button text class="-ml-1" :disabled="!answerText" @click="copyText(answerText)">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </MkTooltip>
      <!-- 进入分享模式 -->
      <span v-if="showShare">
        <MkTooltip content="分享">
          <el-button text :disabled="!canShare" @click="shareLink?.enterShare([message.recordId])">
            <MkIcon name="icon_share_outlined" />
          </el-button>
        </MkTooltip>
      </span>
      <ButtonFeedback v-if="canFeedback" :current-status="currentStatus" :submitting="submitting" @select="openFeedback" />
      <span v-if="meta.createTime" class="text-N600 ml-1">{{ datetimeFormat(meta.createTime) }}</span>
    </div>
    <el-collapse-transition>
      <FeedbackCard
        v-if="draftStatus"
        v-model:reason="reason"
        v-model:content="content"
        :status="draftStatus"
        :submitting="submitting"
        @cancel="draftStatus = undefined"
        @submit="saveFeedback({ vote_status: draftStatus, vote_reason: reason, vote_other_content: reason === 'other' ? content.trim() : '' })"
      />
    </el-collapse-transition>
  </div>
</template>
