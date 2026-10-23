<script setup lang="ts">
import { computed, ref } from 'vue'
import type { OperateLog } from '@/api/types'

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
  <MkDialog v-model="visible" title="API 详情" width="840">
    <pre class="whitespace-pre-wrap break-words p-4">{{ formattedDetails }}</pre>
  </MkDialog>
</template>
