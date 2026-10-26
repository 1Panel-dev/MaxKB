<script setup lang="ts">
import { computed, ref } from 'vue'
import { useApplicationDetailContext } from '../context'
import type { ChatLog } from '@/api/types'
import LogConversation from '@/conversation-panel/view/log/index.vue'

const props = defineProps<{
  chatLog: ChatLog
  loading: boolean
  previousDisabled: boolean
  nextDisabled: boolean
}>()

const { applicationId, resourceApi } = useApplicationDetailContext()
const emit = defineEmits<{ previous: []; next: []; closed: [] }>()

// 对话详情抽屉的打开与关闭
const visible = ref(false)
const conversationContainer = ref<HTMLElement>()
// 执行详情挂到当前抽屉外壳，覆盖标题和翻页区，并随抽屉一起销毁。
const rightDrawerTarget = computed(() => conversationContainer.value?.closest<HTMLElement>('.el-drawer') ?? undefined)

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
  <MkDrawer v-model="visible" size="840" content-class="h-full min-h-0 flex-column p-0!" @close="close" @closed="emit('closed')">
    <template #header>
      <h4 class="min-w-0 truncate" :title="props.chatLog.abstract">{{ props.chatLog.abstract || '-' }}</h4>
    </template>
    <div ref="conversationContainer" v-loading="props.loading" class="min-h-0 flex-1">
      <!-- 只读会话面板:展示该日志的历史对话与执行详情,无输入框 -->
      <LogConversation
        :key="props.chatLog.id"
        :chat-id="props.chatLog.id"
        :application-id="applicationId"
        :chat-log-api="resourceApi.chatLog"
        :right-drawer-target="rightDrawerTarget"
      />
    </div>
    <template #footer>
      <!-- 浏览上一个对话日志 -->
      <el-button plain :disabled="props.previousDisabled || props.loading" @click="handlePrevious">上一个</el-button>
      <!-- 浏览下一个对话日志 -->
      <el-button plain :disabled="props.nextDisabled || props.loading" @click="handleNext">下一个</el-button>
    </template>
  </MkDrawer>
</template>
