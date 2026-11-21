<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { OperateLog } from '@/api/types'

const { t } = useI18n({ useScope: 'global' })

const visible = ref(false)
const operateLog = ref<OperateLog>()
const formattedDetails = computed(() => JSON.stringify(operateLog.value?.details ?? {}, null, 2))

function open(log: OperateLog) {
  operateLog.value = log
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" :title="t('operateLog.apiDetails')" width="840">
    <div class="whitespace-pre-wrap break-words p-4">{{ formattedDetails }}</div>
  </MkDialog>
</template>
