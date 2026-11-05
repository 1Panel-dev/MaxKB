<script setup lang="ts">
import { computed } from 'vue'
import type { ChatFeedback } from '@/api/types'

const props = defineProps<{ feedback: ChatFeedback }>()
const status = computed(() => props.feedback.vote_status)
const reason = computed(() => props.feedback.vote_reason)
const content = computed(() => props.feedback.vote_other_content ?? '')

const reasons = computed(() =>
  props.feedback.vote_status === '0'
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
</script>

<template>
  <div class="mk-gray-card-lg border w-full space-y-3 mb-4">
    <div>
      <h4>{{ status === '0' ? '你觉得什么让你满意？' : '请告诉我们不满意的原因' }}</h4>
    </div>
    <div class="flex flex-wrap gap-2">
      <template v-for="option in reasons" :key="option.value">
        <!-- 只读展示反馈原因 -->
        <el-check-tag :checked="reason === option.value" disabled>
          {{ option.label }}
        </el-check-tag>
      </template>
    </div>
    <el-input v-if="reason === 'other'" :model-value="content" type="textarea" :rows="4" disabled placeholder="告诉我们更多关于你的相关体验" />
  </div>
</template>
