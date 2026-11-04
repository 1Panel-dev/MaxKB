<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ChatFeedback } from '@/api/types'
import type { ChatMessage } from '../../../core/types'
import { useMessageListStore } from '../../message-list'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'MessageFeedback' })

const FEEDBACK_OPTIONS = [
  { status: '0', label: '赞同', icon: 'thumbsup' },
  { status: '1', label: '反对', icon: 'thumbdown' },
] as const

const props = defineProps<{ message: ChatMessage }>()
const { feedback } = useMessageListStore()
const draftStatus = ref<'0' | '1'>()
const reason = ref<ChatFeedback['vote_reason']>(null)
const content = ref('')
const submitting = ref(false)
const currentStatus = computed(() => props.message.record?.feedback?.vote_status ?? '-1')
const reasons = computed(() =>
  draftStatus.value === '0'
    ? ([
        { value: 'accurate', label: '内容准确' },
        { value: 'complete', label: '内容完善' },
        { value: 'other', label: '其他' },
      ] as const)
    : ([
        { value: 'inaccurate', label: '内容不准确' },
        { value: 'incomplete', label: '内容不完善' },
        { value: 'other', label: '其他' },
      ] as const),
)

// 已提交反馈先撤销再重新评价，避免后端重复投票；请求失败保留草稿。
async function saveFeedback(data: ChatFeedback) {
  if (!feedback || !props.message.recordId || submitting.value) return
  const message = props.message
  submitting.value = true
  try {
    await feedback(message.recordId!, data)
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

<template>
  <div v-if="feedback && message.recordId && message.record" class="flex-align-center gap-1">
    <template v-if="feedback && message.recordId && message.record">
      <template v-for="option in FEEDBACK_OPTIONS" :key="option.status">
        <!-- 打开评价面板，再次点击已评价按钮可撤销反馈 -->
        <MkTooltip :content="currentStatus === option.status ? `取消${option.label}` : option.label">
          <el-button
            text
            :disabled="submitting || (currentStatus !== '-1' && currentStatus !== option.status)"
            :class="{ 'text-primary!': currentStatus === option.status || draftStatus === option.status }"
            @click="openFeedback(option.status)"
          >
            <MkIcon :name="`icon_${option.icon}_${currentStatus === option.status ? 'filled' : 'outlined'}`" />
          </el-button>
        </MkTooltip>
      </template>
    </template>
  </div>
  <div v-if="draftStatus" class="mk-gray-card-lg border w-full space-y-3">
    <div class="flex items-center justify-between gap-2">
      <span class="font-medium">{{ draftStatus === '0' ? '你觉得什么让你满意？' : '请告诉我们不满意的原因' }}</span>
      <!-- 关闭反馈填写面板 -->
      <el-button text :disabled="submitting" @click="draftStatus = undefined"><MkIcon name="icon_close_outlined" /></el-button>
    </div>
    <div class="flex flex-wrap gap-2">
      <template v-for="option in reasons" :key="option.value">
        <!-- 选择或取消反馈原因 -->
        <el-check-tag
          type="info"
          :checked="reason === option.value"
          :disabled="submitting"
          @change="reason = reason === option.value ? null : option.value"
        >
          {{ option.label }}
        </el-check-tag>
      </template>
    </div>
    <el-input v-model="content" type="textarea" :rows="3" :disabled="submitting" placeholder="告诉我们更多关于你的相关体验" />
    <div class="text-right">
      <!-- 取消本次反馈 -->
      <el-button class="w-16! min-w-0!" plain :disabled="submitting" @click="draftStatus = undefined">取消</el-button>
      <!-- 提交反馈与补充说明 -->
      <el-button
        class="w-16! min-w-0!"
        type="primary"
        :loading="submitting"
        @click="saveFeedback({ vote_status: draftStatus, vote_reason: reason, vote_other_content: content.trim() })"
      >
        提交
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss"></style>
