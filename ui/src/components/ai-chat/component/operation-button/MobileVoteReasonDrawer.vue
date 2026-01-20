<template>
  <el-drawer
    v-model="visible"
    direction="btt"
    size="-"
    footer-class="mobile-vote-drawer-footer"
    :modal="true"
  >
    <template #header>
      <h4 class="text-center">{{ title }}</h4>
    </template>
    <template #default>
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

      <div v-if="selectedReason === 'other'" class="mt-16">
        <el-input
          v-model="feedBack"
          type="textarea"
          :autosize="{ minRows: 4, maxRows: 20 }"
          :placeholder="$t('chat.vote.placeholder')"
        >
        </el-input>
      </div>
    </template>
    <template #footer>
      <el-space fill wrap :fill-ratio="40" style="width: 100%">
        <el-button @click="visible = false" size="large"> {{ $t('common.cancel') }}</el-button>
        <el-button :disabled="isSubmitDisabled" type="primary" size="large" @click="voteHandle()">
          {{ $t('common.submit') }}</el-button
        >
      </el-space>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { t } from '@/locales'
import chatAPI from '@/api/chat/chat'

const props = defineProps<{
  chatId: string
  recordId: string
  defaultReason?: string
  defaultOtherContent?: string
}>()

const visible = ref(false)
const voteType = ref<string>('') // '0' like, '1' oppose
const selectedReason = ref<string>('')
const feedBack = ref<string>('')
const loading = ref(false)

const selectReason = (value: string) => {
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
  return voteType.value === '0' ? t('chat.vote.likeTitle') : t('chat.vote.opposeTitle')
})

const reasons = computed(() => {
  return voteType.value === '0' ? LIKE_REASONS : OPPOSE_REASONS
})

function voteHandle() {
  chatAPI
    .vote(
      props.chatId,
      props.recordId,
      voteType.value,
      selectedReason.value,
      feedBack.value,
      loading,
    )
    .then(() => {
      emit('success', voteType.value)
      visible.value = false
    })
}

const emit = defineEmits<{
  success: [voteStatus: string]
}>()

const open = (voteStatus: string) => {
  selectedReason.value = ''
  feedBack.value = ''
  voteType.value = voteStatus
  visible.value = true
}

defineExpose({ open })
</script>

<style lang="scss">
.mobile-vote-drawer-footer {
  padding: 0 24px 32px 24px;
  border: none !important;
}
</style>
