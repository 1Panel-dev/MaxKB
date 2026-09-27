<script setup lang="ts">
import { ref } from 'vue'
import type { ChatLog } from '@/api/types'

const props = defineProps<{
  chatLog: ChatLog
  loading: boolean
  previousDisabled: boolean
  nextDisabled: boolean
}>()
const emit = defineEmits<{ previous: []; next: []; closed: [] }>()

// 对话详情抽屉的打开与关闭
const visible = ref(false)

function open() {
  visible.value = true
}

function close() {
  visible.value = false
}

function handlePrevious() {
  if (props.loading || props.previousDisabled) return
  emit('previous')
}

function handleNext() {
  if (props.loading || props.nextDisabled) return
  emit('next')
}

defineExpose({ open, close })
</script>

<template>
  <MkDrawer v-model="visible" size="60%" @close="close" @closed="emit('closed')">
    <template #header>
      <h4 class="min-w-0 truncate" :title="props.chatLog.abstract">{{ props.chatLog.abstract || '对话详情' }}</h4>
    </template>
    <div v-loading="props.loading">对话内容后续接入</div>
    <template #footer>
      <!-- 浏览上一条对话日志 -->
      <el-button plain :disabled="props.previousDisabled || props.loading" @click="handlePrevious">上一条</el-button>
      <!-- 浏览下一条对话日志 -->
      <el-button plain :disabled="props.nextDisabled || props.loading" @click="handleNext">下一条</el-button>
    </template>
  </MkDrawer>
</template>
