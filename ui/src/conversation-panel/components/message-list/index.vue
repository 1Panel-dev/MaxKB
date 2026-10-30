<script setup lang="ts">
import { computed, ref, onBeforeUnmount } from 'vue'
import ContentList from '../content-list/index.vue'
import MessageFooter from '../message-footer/index.vue'
import PrologueContent from '../prologue-content/index.vue'
import { formatPrologue } from '../prologue-content/index'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useMessageListStore } from './index'

defineProps<{ appName?: string }>()

const { appInfo, messages, loading, streamLoading, hasMore, loadMore, onStreamProgress } = useMessageListStore()
const scrollRef = ref<InstanceType<typeof ReverseInfiniteScroll>>()

// 开场白随智能体信息变化（debug 保存后为最新草稿）
const prologue = computed(() => formatPrologue(appInfo.value?.prologue ?? ''))

// 流式分片只在用户仍位于底部时跟随，新增气泡由滚动容器监听 count。
const offProgress = onStreamProgress(() => void scrollRef.value?.followBottom())
onBeforeUnmount(offProgress)
const avatar = computed(() => appInfo.value?.avatar)
const userAvatar = computed(() => appInfo.value?.user_avatar)
const showAvatar = computed(() => appInfo.value?.show_avatar)
const showUserAvatar = computed(() => appInfo.value?.show_user_avatar)
</script>

<template>
  <ReverseInfiniteScroll
    ref="scrollRef"
    content-class="mk-conversation-content p-4"
    :loading="loading"
    :has-more="hasMore"
    :count="messages.length"
    :load-more="loadMore"
  >
    <template #prepend>
      <!-- 开场白在空会话或历史全部加载后显示，固定在会话最前 -->
      <div v-if="prologue && (!messages.length || !hasMore)">
        <ApplicationIcon v-if="showAvatar" :icon="avatar" :size="24" class="shrink-0" />
        <PrologueContent :prologue="prologue" :app-info="appInfo" />
      </div>
    </template>
    <template v-for="(msg, i) in messages" :key="msg.id || i">
      <div>
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
          <!-- 助手消息结束后显示底部信息栏(知识来源/执行详情/tokens/耗时) -->
          <MessageFooter class="mt-3" v-if="msg.role === 'ASSISTANT' && (msg.write_ed || msg.record)" :message="msg" />
        </template>
      </div>
    </template>

    <div v-if="streamLoading">
      <span class="mk-conversation-loading" />
    </div>
  </ReverseInfiniteScroll>
</template>

<style scoped lang="scss"></style>
