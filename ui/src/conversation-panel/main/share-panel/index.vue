<script setup lang="ts">
import { computed } from 'vue'
import ContentList from '../../components/content-list/index.vue'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useMessageListStore } from '../../components/message-list/index'
import { useSharePanelStore } from './index'
import type { ChatMessage } from '../../core/types'

defineOptions({ name: 'SharePanel' })

/** 一轮对话:提问 + 其后的回答，以提问消息 id 作为勾选 key。 */
interface ShareRound {
  key: string
  chatRecordId?: string
  messages: ChatMessage[]
}

const { messages, loading, hasMore, loadMore } = useMessageListStore()
const share = useSharePanelStore()

const shareRounds = computed<ShareRound[]>(() => {
  const rounds: ShareRound[] = []
  messages.value.forEach((message) => {
    const lastRound = rounds[rounds.length - 1]
    if (message.role === 'ASSISTANT' && lastRound && !lastRound.chatRecordId) {
      lastRound.messages.push(message)
      lastRound.chatRecordId = message.recordId
    } else {
      rounds.push({ key: message.id, chatRecordId: message.role === 'ASSISTANT' ? message.recordId : undefined, messages: [message] })
    }
  })
  // 尚未生成 chat_record 的轮次(回答未落库)无法分享
  return rounds.filter((round) => round.chatRecordId)
})

const selectedCount = computed(() => share.selectedRoundKeys.value.length)
const isAllSelected = computed(() => shareRounds.value.length > 0 && selectedCount.value === shareRounds.value.length)
const isIndeterminate = computed(() => selectedCount.value > 0 && !isAllSelected.value)

const handleSelectAll = (checked: boolean | string | number) => share.setSelectedRounds(checked ? shareRounds.value.map((round) => round.key) : [])

const handleShare = () => {
  const chatRecordIds = shareRounds.value.filter((round) => share.isSelected(round.key)).map((round) => round.chatRecordId as string)
  void share.share(chatRecordIds)
}
</script>

<template>
  <!-- 分享主面板:勾选要分享的对话轮次 -->
  <main class="mk-conversation-main">
    <header class="flex-align-center h-11 shrink-0 gap-3 border-b border-N300 px-3">
      <!-- 全选当前已加载的对话 -->
      <el-checkbox :model-value="isAllSelected" :indeterminate="isIndeterminate" :disabled="!shareRounds.length" @change="handleSelectAll">
        全选
      </el-checkbox>
      <span class="min-w-0 flex-1 truncate text-N600">已选择 {{ selectedCount }} 条对话</span>
      <!-- 退出分享模式 -->
      <el-button plain @click="share.close()">取消</el-button>
      <!-- 分享已选对话 -->
      <el-button type="primary" class="ml-0!" :disabled="!selectedCount" :loading="share.sharing.value" @click="handleShare">分享</el-button>
    </header>

    <ReverseInfiniteScroll class="p-4" :loading="loading" :has-more="hasMore" :count="shareRounds.length" :load-more="loadMore">
      <!-- 点击整轮对话切换勾选 -->
      <div
        v-for="round in shareRounds"
        :key="round.key"
        class="share-round flex cursor-pointer gap-3 rounded-lg p-2"
        :class="{ selected: share.isSelected(round.key) }"
        @click="share.toggleRound(round.key)"
      >
        <el-checkbox :model-value="share.isSelected(round.key)" class="pointer-events-none shrink-0" />
        <!-- 分享模式下内容只读，不响应内部交互 -->
        <div class="pointer-events-none min-w-0 flex-1 select-none">
          <ContentList v-for="message in round.messages" :key="message.id" :content-list="message.content" />
        </div>
      </div>

      <template #empty>
        <MkEmpty description="暂无可分享的对话" class="mt-20" />
      </template>
    </ReverseInfiniteScroll>
  </main>
</template>

<style scoped lang="scss">
.share-round {
  transition: background-color 150ms ease;

  &:hover {
    background: var(--mk-N100);
  }

  &.selected {
    background: color-mix(in srgb, var(--mk-primary) 6%, transparent);
  }
}
</style>
