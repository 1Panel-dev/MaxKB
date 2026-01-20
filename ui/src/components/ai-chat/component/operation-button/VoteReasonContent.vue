<template>
  <div>
    <h4>{{ title }}</h4>
    <div class="mt-16">
      <el-space wrap :size="12">
        <template v-for="reason in reasons" :key="reason.value">
          <el-check-tag
            type="primary"
            :checked="selectedReason === reason.value"
            @change="selectReason(reason.value)"
          >
            {{ reason.label }}</el-check-tag
          >
        </template>
      </el-space>
    </div>
    <div v-if="selectedReason === 'other'" class="mt-16">
      <el-input
        v-model="feedBack"
        type="textarea"
        :autosize="{ minRows: 4, maxRows: 20 }"
        :placeholder="$t('chat.vote.placeholder')"
        :readonly="readonly"
      >
      </el-input>
    </div>
    <div v-if="!readonly" class="dialog-footer mt-24 text-right">
      <el-button @click="emit('close')"> {{ $t('common.cancel') }}</el-button>
      <el-button :disabled="isSubmitDisabled" type="primary" @click="voteHandle()">
        {{ $t('common.submit') }}</el-button
      >
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { t } from '@/locales'
import chatAPI from '@/api/chat/chat'

const props = defineProps<{
  voteType: '0' | '1'
  chatId: string
  recordId: string
  readonly?: boolean
  defaultReason?: string
  defaultOtherContent?: string
}>()

const selectedReason = ref<string>(props.readonly ? props.defaultReason || '' : '')
const feedBack = ref<string>(props.readonly ? props.defaultOtherContent || '' : '')
const loading = ref(false)

const selectReason = (value: string) => {
  if (props.readonly) {
    return
  }
  selectedReason.value = value
}

const isSubmitDisabled = computed(() => {
  if (!selectedReason.value) {
    return true
  }
  if (selectedReason.value === 'other' && !feedBack.value.trim()) {
    return true
  }
  return false
})

const LIKE_REASONS = [
  { label: t('chat.vote.accurate'), value: 'accurate' },
  { label: t('chat.vote.complete'), value: 'complete' },
  { label: t('chat.vote.other'), value: 'other' },
]

const OPPOSE_REASONS = [
  { label: t('chat.vote.inaccurate'), value: 'inaccurate' },
  { label: t('chat.vote.irrelevantAnswer'), value: 'incomplete' },
  { label: t('chat.vote.other'), value: 'other' },
]

const title = computed(() => {
  return props.voteType === '0' ? t('chat.vote.likeTitle') : t('chat.vote.opposeTitle')
})

const reasons = computed(() => {
  return props.voteType === '0' ? LIKE_REASONS : OPPOSE_REASONS
})

function voteHandle() {
  chatAPI
    .vote(
      props.chatId,
      props.recordId,
      props.voteType,
      selectedReason.value,
      feedBack.value,
      loading,
    )
    .then(() => {
      emit('success', props.voteType)
      emit('close')
    })
}

const emit = defineEmits<{
  success: [voteStatus: string]
  close: []
}>()
</script>

<style lang="scss" scoped></style>
