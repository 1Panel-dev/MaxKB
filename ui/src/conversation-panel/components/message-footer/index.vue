<template>
  <!-- 助手消息底部信息栏:知识来源 / 执行详情 / Tokens · 耗时 -->
  <div class="msg-footer">
    <template v-if="meta.knowledgeCount">
      <span class="msg-footer__item">知识来源 ({{ meta.knowledgeCount }})</span>
      <span class="msg-footer__sep">|</span>
    </template>
    <!-- 执行详情:对话结束时已拉取并缓存,点击直接在右侧展示 -->
    <span class="msg-footer__item msg-footer__link" @click="openExecutionDetail">执行详情</span>
    <template v-if="meta.runTime || tokens">
      <span class="msg-footer__sep">|</span>
      <span class="msg-footer__item">Tokens {{ tokens }} · 耗时 {{ meta.runTime.toFixed(2) }}s</span>
    </template>
  </div>
</template>

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

<style scoped lang="scss">
.msg-footer {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
  font-size: 12px;
  color: var(--t3, #909399);
}
.msg-footer__item {
  display: inline-flex;
  align-items: center;
}
.msg-footer__link {
  cursor: pointer;
  color: var(--t2, #606266);
}
.msg-footer__link:hover {
  color: var(--el-color-primary, #3370ff);
}
.msg-footer__sep {
  color: var(--bd, #dcdfe6);
}
</style>
