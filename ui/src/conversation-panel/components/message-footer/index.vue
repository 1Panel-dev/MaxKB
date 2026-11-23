<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatMessage, ChatRecordMeta } from '../../core/types'
import type { ChatContent, ChatFeedback } from '@/api/types'
import { useRightSidebarStore } from '../../right-sidebar/index'
import { DEVICE_TYPE, useDeviceType, useShowShare } from '../../view/index'
import { MESSAGE_LIST_KEY } from '../message-list/index'
import { useShareLinkStoreOptional } from '../message-list/share/index'
import ButtonFeedback from './feedback/ButtonFeedback.vue'
import FeedbackCard from './feedback/FeedbackCard.vue'
import { copyText } from '@/utils/clipboard'
import { MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'

const props = defineProps<{ message: ChatMessage }>()
const emit = defineEmits<{ resize: [] }>()
const { t } = useI18n({ useScope: 'global' })
const deviceType = useDeviceType()
const footerRef = ref<HTMLElement>()

// 反馈展开动画逐帧改变高度，由消息列表决定是否继续跟随底部。
let footerObserver: ResizeObserver | undefined
onMounted(() => {
  footerObserver = new ResizeObserver(() => emit('resize'))
  if (footerRef.value) footerObserver.observe(footerRef.value)
})
onBeforeUnmount(() => footerObserver?.disconnect())
// 智能体允许分享时显示分享入口；进入分享时预先勾选当前回答所属轮次。
const showShare = useShowShare()
const shareLink = useShareLinkStoreOptional()

// 回答生成中禁用分享。
const messageList = inject(MESSAGE_LIST_KEY, null)
const canShare = computed(() => Boolean(messageList?.messages.value.length && !messageList.streamLoading.value))
const show_exec = computed(() => messageList?.appInfo.value?.show_exec)
const tts_model_enable = computed(() => messageList?.appInfo.value?.tts_model_enable)
const rightSidebar = useRightSidebarStore()

const EMPTY: ChatRecordMeta = {
  messageTokens: 0,
  answerTokens: 0,
  runTime: 0,
  paragraphList: [],
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

// 重新生成沿用当前记录及原问题，由列表 Store 管理流式替换。
const canRegenerate = computed(() => Boolean(messageList && props.message.recordId && !messageList.streamLoading.value && !messageList.loading.value))
function regenerateAnswer() {
  if (!canRegenerate.value) return
  stopReading()
  messageList?.regenerate(props.message)
}

// 朗读回答正文，由消息列表统一管理：与自动播放共用状态，同一时间只读一条，按智能体设置选择浏览器或模型语音。
// 点击在朗读、暂停、继续间切换；底部栏在生成中隐藏，卸载时不停止朗读，新发送、切换会话或离开时由消息列表停止。
const speechSupported = computed(() => Boolean(messageList?.speechSupported.value))
const reading = computed(() => Boolean(messageList && messageList.speakingMessage.value === props.message))
const readingPaused = computed(() => reading.value && Boolean(messageList?.speechPaused.value))
const readingTip = computed(() =>
  !reading.value ? t('chat.voice.readContent') : readingPaused.value ? t('chat.voice.resumeReading') : t('chat.voice.pauseReading'),
)
function stopReading() {
  if (reading.value) messageList?.stopSpeech()
}
function toggleReading() {
  if (readingPaused.value) return messageList?.resumeSpeech()
  if (reading.value) return messageList?.pauseSpeech()
  if (speechSupported.value && answerText.value) messageList?.playSpeech(props.message, answerText.value)
}

const openExecutionDetail = () => {
  rightSidebar.showExecutionDetail(meta.value.executionDetails || [])
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
    MsgSuccess(data.vote_status === '-1' ? t('chat.feedback.cancelledMessage') : t('chat.feedback.thanksMessage'))
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
      <!-- 知识来源:在右侧展示回答引用的分段 -->
      <el-button v-if="meta.paragraphList.length" text class="-ml-1" @click="rightSidebar.showKnowledgeSource(meta.paragraphList)">
        <MkIcon name="icon_reference_outlined" />
        <span>
          <template v-if="deviceType !== DEVICE_TYPE.MOBILE">{{ t('chat.knowledgeSource.label') }}</template>
          ({{ meta.paragraphList.length }})
        </span>
      </el-button>

      <!-- 执行详情:对话结束时已拉取并缓存,点击直接在右侧展示 -->
      <el-button v-if="show_exec" text @click="openExecutionDetail" class="-ml-1">
        <MkIcon name="icon_logs_outlined" />
        <span v-if="deviceType !== DEVICE_TYPE.MOBILE">{{ t('execution.details.title') }}</span>
      </el-button>
      <template v-if="meta.runTime || tokens">
        <el-divider v-if="meta.paragraphList.length || show_exec" direction="vertical" class="ml-2! mr-3!" />
        <span class="text-N600">Tokens {{ tokens }} · {{ t('common.labels.duration') }} {{ meta.runTime.toFixed(2) }}s</span>
      </template>
    </div>
    <!-- 其他操作 -->
    <div class="flex-align-center flex-wrap gap-2">
      <!-- 复制回答正文 -->
      <MkTooltip :content="t('common.actions.copy')">
        <el-button text class="-ml-1" :disabled="!answerText" @click="copyText(answerText, t('common.messages.copied'))">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </MkTooltip>
      <!-- 重新生成当前回答 -->
      <span>
        <MkTooltip :content="t('common.actions.regenerate')">
          <el-button text :disabled="!canRegenerate" @click="regenerateAnswer">
            <MkIcon name="icon_refresh_outlined" />
          </el-button>
        </MkTooltip>
      </span>

      <!-- 朗读回答正文，再次点击停止 -->
      <span v-if="tts_model_enable">
        <MkTooltip :content="readingTip">
          <el-button text :disabled="!reading && (!speechSupported || !answerText)" @click="toggleReading">
            <VoiceWaveIcon v-if="reading && !readingPaused" :size="16" class="text-primary" />
            <MkIcon v-else name="icon_speaker_outlined" />
          </el-button>
        </MkTooltip>
      </span>
      <ButtonFeedback v-if="canFeedback" :current-status="currentStatus" :submitting="submitting" @select="openFeedback" />
      <!-- 进入分享模式 -->
      <span v-if="showShare">
        <MkTooltip :content="t('chat.share.label')">
          <el-button text :disabled="!canShare" @click.stop.prevent="shareLink?.enterShare([message.recordId])">
            <MkIcon name="icon_share_outlined" />
          </el-button>
        </MkTooltip>
      </span>
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
