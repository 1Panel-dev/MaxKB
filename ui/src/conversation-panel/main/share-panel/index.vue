<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '../../core/types'
import ContentList from '../../components/content-list/index.vue'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useSharePanelContentStore } from './index'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'SharePanel' })

const { appInfo, messages, loading, title, hasMore, loadMore } = useSharePanelContentStore()
const copyMessage = (message: ChatMessage) =>
  copyText(
    message.content
      .map((content) => content.content || '')
      .filter(Boolean)
      .join('\n'),
  )
const avatar = computed(() => appInfo.value?.avatar)
const userAvatar = computed(() => appInfo.value?.user_avatar)
const showAvatar = computed(() => appInfo.value?.show_avatar)
const showUserAvatar = computed(() => appInfo.value?.show_user_avatar)
</script>

<template>
  <!-- 分享主面板：只读展示对话记录 -->
  <main class="mk-conversation-main">
    <header class="mk-conversation-chat-header flex-align-center gap-3 p-4">
      <div class="min-w-0 flex-1">
        <h4 class="truncate">{{ title }}</h4>
      </div>
    </header>
    <ReverseInfiniteScroll
      content-class="mk-conversation-content p-4 space-y-2"
      :loading="loading"
      :has-more="hasMore"
      :count="messages.length"
      :load-more="loadMore"
    >
      <p v-if="appInfo?.disclaimer" class="wrap-anywhere text-center text-sm text-N500 mb-4">{{ appInfo?.disclaimer_value }}</p>

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
        <template v-else>
          <ApplicationIcon v-if="showAvatar" :icon="avatar" :size="24" class="shrink-0" />
          <ContentList :content-list="msg.content" />
          <!-- 复制回答正文 -->
          <MkTooltip content="复制">
            <el-button text class="-ml-1" :disabled="!msg.content.length" @click="copyMessage(msg)">
              <MkIcon name="icon_copy_outlined" />
            </el-button>
          </MkTooltip>
        </template>
      </template>
      <template #empty>
        <MkEmpty description="暂无可分享的对话" class="mt-20" />
      </template>
    </ReverseInfiniteScroll>
  </main>
</template>
