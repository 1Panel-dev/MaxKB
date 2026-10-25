<script setup lang="ts">
import { ref, onBeforeUnmount } from 'vue'
import ContentList from '../content-list/index.vue'
import MessageFooter from '../message-footer/index.vue'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useMessageListStore } from './index'

defineProps<{ appName?: string }>()

const { messages, loading, streamLoading, hasMore, loadMore, onStreamProgress } = useMessageListStore()
const scrollRef = ref<InstanceType<typeof ReverseInfiniteScroll>>()

// 流式分片只在用户仍位于底部时跟随，新增气泡由滚动容器监听 count。
const offProgress = onStreamProgress(() => void scrollRef.value?.followBottom())
onBeforeUnmount(offProgress)
</script>

<template>
  <ReverseInfiniteScroll ref="scrollRef" class="p-4" :loading="loading" :has-more="hasMore" :count="messages.length" :load-more="loadMore">
    <template v-for="(msg, i) in messages" :key="msg.id || i">
      <div :class="[msg.role === 'USER' ? 'user' : 'assistant']">
        <ContentList :content-list="msg.content" />
        <!-- 助手消息结束后显示底部信息栏(知识来源/执行详情/tokens/耗时) -->
        <MessageFooter v-if="msg.role === 'ASSISTANT' && (msg.write_ed || msg.record)" :message="msg" />
      </div>
    </template>

    <div v-if="streamLoading" class="msg-row assistant">
      <span class="mk-conversation-loading" />
    </div>

    <template #empty>
      <div class="welcome">
        <slot name="welcome">
          <p class="welcome-title">{{ appName }}</p>
          <p class="welcome-sub">有什么可以帮你的？</p>
        </slot>
      </div>
    </template>
  </ReverseInfiniteScroll>
</template>

<style scoped lang="scss">
// .message-list {
//   flex: 1;
//   min-height: 0;
//   overflow-y: auto;
//   padding: 14px 12px;
//   scrollbar-width: thin;
//   display: flex;
//   flex-direction: column;
//   align-items: center;
// }

// .message-list__more {
//   display: flex;
//   justify-content: center;
//   padding: 4px 0 10px;
//   color: var(--t3, #909399);
// }

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

// .msg-row {
//   display: flex;
//   flex-direction: column;
//   gap: 6px;
//   margin-bottom: 10px;
//   max-width: 800px;
//   width: 100%;
//   box-sizing: border-box;
// }
// .msg-row.user {
//   align-items: flex-end;
//   flex-direction: row-reverse;
// }
// .msg-row.assistant {
//   align-items: flex-start;
// }
</style>
