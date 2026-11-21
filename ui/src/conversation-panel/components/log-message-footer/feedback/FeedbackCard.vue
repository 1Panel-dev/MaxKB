<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatFeedback } from '@/api/types'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ feedback: ChatFeedback }>()
const status = computed(() => props.feedback.vote_status)
const reason = computed(() => props.feedback.vote_reason)
const content = computed(() => props.feedback.vote_other_content ?? '')

const reasons = computed(() =>
  props.feedback.vote_status === '0'
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
    <div>
      <h4>{{ status === '0' ? t('chat.feedback.positiveTitle') : t('chat.feedback.negativeTitle') }}</h4>
    </div>
    <div class="flex flex-wrap gap-2">
      <template v-for="option in reasons" :key="option.value">
        <!-- 只读展示反馈原因 -->
        <el-check-tag :checked="reason === option.value" disabled>
          {{ option.label }}
        </el-check-tag>
      </template>
    </div>
    <el-input v-if="reason === 'other'" :model-value="content" type="textarea" :rows="4" disabled :placeholder="t('chat.feedback.placeholder')" />
  </div>
</template>
