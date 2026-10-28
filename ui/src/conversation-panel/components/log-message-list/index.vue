<script setup lang="ts">
import { computed } from 'vue'
import ContentList from '../content-list/index.vue'
import MessageFooter from '../message-footer/index.vue'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useLogMessageListStore } from './index'

const { appInfo, messages, loading, hasMore, loadMore } = useLogMessageListStore()
const avatar = computed(() => appInfo.value?.avatar)
const userAvatar = computed(() => appInfo.value?.user_avatar)
const showAvatar = computed(() => appInfo.value?.show_avatar)
const showUserAvatar = computed(() => appInfo.value?.show_user_avatar)
</script>

<template>
  <ReverseInfiniteScroll content-class="p-4" :loading="loading" :has-more="hasMore" :count="messages.length" :load-more="loadMore">
    <template v-for="(msg, i) in messages" :key="msg.id || i">
      <!-- 用户提问靠右：头像独占一行在上，提问容器在下方靠右收缩 -->
      <div v-if="msg.role === 'USER'">
        <div v-if="showUserAvatar" class="text-right">
          <el-avatar v-if="userAvatar" class="bg-transparent!" shape="square" :size="24">
            <img :src="userAvatar" alt="" />
          </el-avatar>
          <el-avatar v-else :size="24" :style="{ background: appInfo?.custom_theme?.theme_color || 'var(--mk-primary-gradient)' }">
            <img src="@/assets/mk_icon_user_gradient.svg" alt="" style="width: 50%" />
          </el-avatar>
        </div>
        <ContentList :content-list="msg.content" />
      </div>
      <div v-else>
        <ApplicationIcon v-if="showAvatar" :icon="avatar" :size="24" class="shrink-0" />
        <ContentList :content-list="msg.content" />
        <!-- 助手消息底部信息栏(知识来源/执行详情/tokens/耗时) -->
        <MessageFooter class="mt-3" v-if="msg.role === 'ASSISTANT' && msg.record" :message="msg" />
      </div>
    </template>

    <template #empty>
      <el-empty class="flex-1" description="暂无对话记录" :image-size="80" />
    </template>
  </ReverseInfiniteScroll>
</template>
