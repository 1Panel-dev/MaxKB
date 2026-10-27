<script setup lang="ts">
import { computed, ref, onBeforeUnmount } from 'vue'
import ContentList from '../content-list/index.vue'
import MessageFooter from '../message-footer/index.vue'
import PrologueContent from '../prologue-content/index.vue'
import { formatPrologue } from '../prologue-content/index'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useMessageListStore } from './index'
import { te } from 'element-plus/es/locale/index.mjs'

defineProps<{ appName?: string }>()

const { appInfo, messages, loading, streamLoading, hasMore, loadMore, onStreamProgress } = useMessageListStore()
const scrollRef = ref<InstanceType<typeof ReverseInfiniteScroll>>()

// 开场白随智能体信息变化（debug 保存后为最新草稿）
const prologue = computed(() => formatPrologue(appInfo.value?.prologue ?? ''))

// 流式分片只在用户仍位于底部时跟随，新增气泡由滚动容器监听 count。
const offProgress = onStreamProgress(() => void scrollRef.value?.followBottom())
onBeforeUnmount(offProgress)
const avatar = computed(() => appInfo.value?.avatar)
const user_avatar = computed(() => appInfo.value?.user_avatar)
const show_avatar = computed(() => appInfo.value?.show_avatar)
const show_user_avatar = computed(() => appInfo.value?.show_user_avatar)
</script>

<template>
  <ReverseInfiniteScroll ref="scrollRef" content-class="p-4" :loading="loading" :has-more="hasMore"
    :count="messages.length" :load-more="loadMore">
    <!-- 开场白固定在会话最前，历史全部加载后才显示，避免夹在已加载的消息之间 -->
    <div v-if="prologue && !hasMore">
       <ApplicationIcon v-if="show_avatar" :icon="avatar" :size="24" class="shrink-0 mr-2" />
      <PrologueContent :prologue="prologue" :app-info="appInfo" />
    </div>
    <template v-for="(msg, i) in messages" :key="msg.id || i">
      <div>
        <!-- 用户提问靠右：头像独占一行在上，提问容器在下方靠右收缩 -->
        <div v-if="msg.role === 'USER'" class="flex flex-col items-end">
          <ApplicationIcon v-if="show_user_avatar" :icon="user_avatar" :size="24" class="mb-2" />
          <ContentList :content-list="msg.content" />
          <!-- 这块写用户的操作 -->
        </div>
        <template v-else>
          <ApplicationIcon v-if="show_avatar" :icon="avatar" :size="24" class="shrink-0 mr-2" />
          <ContentList :content-list="msg.content" />
          <!-- 助手消息结束后显示底部信息栏(知识来源/执行详情/tokens/耗时) -->
          <MessageFooter v-if="msg.role === 'ASSISTANT' && (msg.write_ed || msg.record)" :message="msg" />
        </template>
      </div>
    </template>

    <div v-if="streamLoading">
      <span class="mk-conversation-loading" />
    </div>

    <template #empty>
      <!-- 有开场白时按首条助手消息展示，否则显示欢迎语 -->
      <div v-if="prologue">
        <ApplicationIcon v-if="show_avatar" :icon="avatar" :size="24" class="shrink-0 mr-2" />
        <PrologueContent :prologue="prologue" :app-info="appInfo" />
      </div>
    </template>
  </ReverseInfiniteScroll>
</template>

<style scoped lang="scss">
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
</style>
