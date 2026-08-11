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
  <el-dialog v-model="visible" title="日志详情" width="720" destroy-on-close>
    <el-scrollbar height="400px" class="rounded border">
      <pre class="whitespace-pre-wrap break-words p-4">{{ formattedDetails }}</pre>
    </el-scrollbar>
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>
