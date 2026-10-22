<template>
  <!-- 接口加载:无消息时(首页)整块遮罩,有消息时(加载更多)顶部小转圈;对话加载:底部小点 -->
  <div ref="msgBoxRef" v-loading="fullLoading" class="message-list" @scroll="onScroll">
    <template v-if="messages.length > 0">
      <div v-if="loading" class="message-list__more">
        <el-icon class="is-loading" :size="18"><LoadingIcon /></el-icon>
      </div>

      <div v-for="(msg, i) in messages" :key="msg.id || i" :class="['msg-row', msg.role === 'USER' ? 'user' : 'assistant']">
        <ContentList :content-list="msg.content" />
        <!-- 助手消息结束后显示底部信息栏(知识来源/执行详情/tokens/耗时) -->
        <MessageFooter v-if="msg.role === 'ASSISTANT' && (msg.write_ed || msg.record)" :message="msg" />
      </div>

      <div v-if="streamLoading" class="msg-row assistant">
        <Loading :size="18" />
      </div>
    </template>

    <div v-else-if="!loading" class="welcome">
      <slot name="welcome">
        <p class="welcome-title">{{ appName }}</p>
        <p class="welcome-sub">有什么可以帮你的？</p>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { Loading as LoadingIcon } from '@element-plus/icons-vue'
import ContentList from '../content-list/index.vue'
import MessageFooter from '../message-footer/index.vue'
import Loading from '../../loading/index.vue'
import { Scroll } from '../../core/stream'
import { useMessageListStore } from './index'

defineProps<{ appName?: string }>()

const { messages, loading, streamLoading, hasMore, loadMore, onStreamProgress } = useMessageListStore()

// 整块遮罩:切换会话会先清空消息,故无消息时的接口加载即首页加载
const fullLoading = computed(() => loading.value && messages.value.length === 0)

const msgBoxRef = ref<HTMLElement | null>(null)
let scroll: Scroll | null = null
let offProgress: (() => void) | null = null

onMounted(() => {
  if (msgBoxRef.value) scroll = new Scroll(msgBoxRef.value)
  // 流式分片(on_next)→ 吸底。适配所有流来源(发送 / 续传),不依赖 message-input。
  offProgress = onStreamProgress(() => nextTick(() => scroll?.scrollBottom()))
})
onBeforeUnmount(() => offProgress?.())

// 新增气泡(提问 / 新回答)→ 吸底
watch(
  () => messages.value.length,
  () => nextTick(() => scroll?.scrollBottom()),
)

// 上滑到顶 → 加载更多
const onScroll = () => {
  const el = msgBoxRef.value
  if (el && el.scrollTop <= 60 && hasMore.value) loadMore()
}
</script>

<style scoped lang="scss">
.message-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 14px 12px;
  scrollbar-width: thin;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.message-list__more {
  display: flex;
  justify-content: center;
  padding: 4px 0 10px;
  color: var(--t3, #909399);
}

.welcome {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 32px 16px;
}
.welcome-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--t1, #303133);
  margin-bottom: 8px;
}
.welcome-sub {
  font-size: 14px;
  color: var(--t3, #909399);
}

.msg-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
  max-width: 800px;
  width: 100%;
  box-sizing: border-box;
}
.msg-row.user {
  align-items: flex-end;
  flex-direction: row-reverse;
}
.msg-row.assistant {
  align-items: flex-start;
}
</style>
