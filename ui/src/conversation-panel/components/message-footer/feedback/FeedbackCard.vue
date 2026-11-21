<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatFeedback } from '@/api/types'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ status: '0' | '1'; submitting: boolean }>()
const reason = defineModel<ChatFeedback['vote_reason']>('reason', { required: true })
const content = defineModel<string>('content', { required: true })
const emit = defineEmits<{ cancel: []; submit: [] }>()

const reasons = computed(() =>
  props.status === '0'
    ? ([
        { value: 'accurate', label: t('chat.feedback.reasons.accurate') },
        { value: 'complete', label: t('chat.feedback.reasons.complete') },
        { value: 'other', label: t('common.labels.other') },
      ] as const)
    : ([
        { value: 'inaccurate', label: t('chat.feedback.reasons.inaccurate') },
        { value: 'incomplete', label: t('chat.feedback.reasons.incomplete') },
        { value: 'other', label: t('common.labels.other') },
      ] as const),
)
</script>

<template>
  <div class="mk-gray-card-lg border w-full space-y-3 mb-4">
    <div class="flex items-center justify-between gap-2">
      <h4>{{ status === '0' ? t('chat.feedback.positiveTitle') : t('chat.feedback.negativeTitle') }}</h4>
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
      :placeholder="t('chat.feedback.placeholder')"
    />
    <div class="text-right">
      <!-- 取消本次反馈 -->
      <el-button class="w-16! min-w-0!" plain :disabled="submitting" @click="emit('cancel')">{{ t('common.actions.cancel') }}</el-button>
      <!-- 提交反馈与补充说明 -->
      <el-button
        class="w-16! min-w-0!"
        type="primary"
        :loading="submitting"
        :disabled="!reason || (reason === 'other' && !content.trim())"
        @click="emit('submit')"
      >
        {{ t('common.actions.submit') }}
      </el-button>
    </div>
  </div>
</template>
