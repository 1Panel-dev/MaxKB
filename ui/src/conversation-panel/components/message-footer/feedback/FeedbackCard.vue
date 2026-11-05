<script setup lang="ts">
import { computed } from 'vue'
import type { ChatFeedback } from '@/api/types'

const props = defineProps<{ status: '0' | '1'; submitting: boolean }>()
const reason = defineModel<ChatFeedback['vote_reason']>('reason', { required: true })
const content = defineModel<string>('content', { required: true })
const emit = defineEmits<{ cancel: []; submit: [] }>()

const reasons = computed(() =>
  props.status === '0'
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
    <div class="flex items-center justify-between gap-2">
      <h4>{{ status === '0' ? '你觉得什么让你满意？' : '请告诉我们不满意的原因' }}</h4>
      <!-- 关闭反馈填写面板 -->
      <el-button text :disabled="submitting" @click="emit('cancel')"><MkIcon name="icon_close_outlined" /></el-button>
    </div>
    <div class="flex flex-wrap gap-2">
      <template v-for="option in reasons" :key="option.value">
        <!-- 选择或取消反馈原因 -->
        <el-check-tag :checked="reason === option.value" :disabled="submitting" @change="reason = reason === option.value ? null : option.value">
          {{ option.label }}
        </el-check-tag>
      </template>
    </div>
    <el-input
      v-if="reason === 'other'"
      v-model="content"
      type="textarea"
      :rows="4"
      :disabled="submitting"
      placeholder="告诉我们更多关于你的相关体验"
    />
    <div class="text-right">
      <!-- 取消本次反馈 -->
      <el-button class="w-16! min-w-0!" plain :disabled="submitting" @click="emit('cancel')">取消</el-button>
      <!-- 提交反馈与补充说明 -->
      <el-button
        class="w-16! min-w-0!"
        type="primary"
        :loading="submitting"
        :disabled="!reason || (reason === 'other' && !content.trim())"
        @click="emit('submit')"
      >
        提交
      </el-button>
    </div>
  </div>
</template>
