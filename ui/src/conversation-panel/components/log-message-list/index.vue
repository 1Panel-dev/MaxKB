<script setup lang="ts">
import ContentList from '../content-list/index.vue'
import MessageFooter from '../message-footer/index.vue'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useLogMessageListStore } from './index'

const { messages, loading, hasMore, loadMore } = useLogMessageListStore()
</script>

<template>
  <ReverseInfiniteScroll content-class="p-4" :loading="loading" :has-more="hasMore" :count="messages.length" :load-more="loadMore">
    <template v-for="(msg, i) in messages" :key="msg.id || i">
      <!-- msg.role === 'USER' -->
      <div>
        <ContentList :content-list="msg.content" />
        <!-- 助手消息底部信息栏(知识来源/执行详情/tokens/耗时) -->
        <MessageFooter v-if="msg.role === 'ASSISTANT' && msg.record" :message="msg" />
      </div>
    </template>

    <template #empty>
      <el-empty class="flex-1" description="暂无对话记录" :image-size="80" />
    </template>
  </ReverseInfiniteScroll>
</template>
