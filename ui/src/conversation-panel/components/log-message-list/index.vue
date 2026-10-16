<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { Loading as LoadingIcon } from '@element-plus/icons-vue'
import ContentList from '../content-list/index.vue'
import MessageFooter from '../message-footer/index.vue'
import { Scroll } from '../../core/stream'
import { useLogMessageListStore } from './index'

const { messages, loading, hasMore, loadMore } = useLogMessageListStore()

// 整块遮罩:load 会先清空消息,故无消息时的加载即首页加载
const fullLoading = computed(() => loading.value && messages.value.length === 0)

const msgBoxRef = ref<HTMLElement | null>(null)
let scroll: Scroll | null = null
onMounted(() => {
  if (msgBoxRef.value) scroll = new Scroll(msgBoxRef.value)
})

// 首页加载完成(消息从无到有)→ 定位到最新一条
watch(
  () => messages.value.length,
  (len, prevLen) => {
    if (len > 0 && !prevLen) nextTick(() => scroll?.forceBottom())
  },
)

// 上滑到顶加载更早的记录,并保持当前阅读位置不跳动
const onScroll = async () => {
  const el = msgBoxRef.value
  if (!el || el.scrollTop > 60 || !hasMore.value || loading.value) return
  const prevHeight = el.scrollHeight
  await loadMore()
  await nextTick()
  el.scrollTop += el.scrollHeight - prevHeight
}
</script>

<template>
  <!-- 只读会话记录:首页加载整块遮罩,上滑加载更多时顶部小转圈 -->
  <div ref="msgBoxRef" v-loading="fullLoading" class="log-message-list p-6" @scroll="onScroll">
    <template v-if="messages.length > 0">
      <div v-if="loading" class="log-message-list__more">
        <el-icon class="is-loading" :size="18"><LoadingIcon /></el-icon>
      </div>

      <div v-for="(msg, i) in messages" :key="msg.id || i" :class="['msg-row', msg.role === 'USER' ? 'user' : 'assistant']">
        <ContentList :content-list="msg.content" />
        <!-- 助手消息底部信息栏(知识来源/执行详情/tokens/耗时) -->
        <MessageFooter v-if="msg.role === 'ASSISTANT' && msg.record" :message="msg" />
      </div>
    </template>

    <el-empty v-else-if="!loading" class="flex-1" description="暂无对话记录" :image-size="80" />
  </div>
</template>

<style scoped lang="scss">
.log-message-list {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  scrollbar-width: thin;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.log-message-list__more {
  display: flex;
  justify-content: center;
  padding: 4px 0 10px;
  color: var(--t3, #909399);
}

.msg-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
  max-width: 680px;
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
