<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage, ChatRecordMeta } from '../../core/types'
import { useExecutionDetailStore } from '../../right-sidebar/execution-detail/index'

const props = defineProps<{ message: ChatMessage }>()

const detail = useExecutionDetailStore()

const EMPTY: ChatRecordMeta = {
  messageTokens: 0,
  answerTokens: 0,
  runTime: 0,
  knowledgeCount: 0,
  executionDetails: [],
}
const meta = computed<ChatRecordMeta>(() => props.message.record || EMPTY)
const tokens = computed(() => meta.value.messageTokens + meta.value.answerTokens)

const openExecutionDetail = () => {
  detail.showExecutionDetail(meta.value.executionDetails || [])
}
</script>

<style scoped lang="scss"></style>

<template>
  <!-- 助手消息底部信息栏:知识来源 / 执行详情 / Tokens · 耗时  -->
  <div class="msg-footer flex-align-center gap-1">
    <el-button v-if="meta.knowledgeCount" text class="-ml-1">
      <MkIcon name=" icon_reference_outlined" />
      <span>知识来源 ({{ meta.knowledgeCount }})</span>
    </el-button>

    <!-- 执行详情:对话结束时已拉取并缓存,点击直接在右侧展示 -->
    <el-button text @click="openExecutionDetail" class="-ml-1">
      <MkIcon name="icon_logs_outlined" />
      <span>执行详情</span>
    </el-button>
    <template v-if="meta.runTime || tokens">
      <el-divider direction="vertical" class="ml-2! mr-3!" />
      <span class="text-N600">Tokens {{ tokens }} · 耗时 {{ meta.runTime.toFixed(2) }}s</span>
    </template>
  </div>
</template>
