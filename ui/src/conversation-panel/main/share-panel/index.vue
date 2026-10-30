<script setup lang="ts">
import { computed } from 'vue'
import ContentList from '../../components/content-list/index.vue'
import ReverseInfiniteScroll from '../../core/reverse-infinite-scroll/index.vue'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
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
const list = useConversationListStore()

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
    <header class="mk-conversation-chat-header flex-align-center gap-3 p-4">
      <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
      <template v-if="!list.leftSideOpen.value">
        <!-- 展开左侧 -->
        <MkTooltip content="展开侧边栏">
          <el-button text @click="list.toggleLeftSide()" class="-ml-1">
            <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
          </el-button>
        </MkTooltip>
      </template>

      <div class="flex-1 flex-align-center gap-2">
        <h4 class="truncate">{{ list.currentConversation.value?.abstract || '新建对话' }}</h4>
      </div>
    </header>
    <ReverseInfiniteScroll
      content-class="mk-conversation-content p-4 space-y-2"
      :loading="loading"
      :has-more="hasMore"
      :count="shareRounds.length"
      :load-more="loadMore"
    >
      <template v-for="round in shareRounds" :key="round.key">
        <!-- 点击整轮对话切换勾选 -->
        <div class="group flex cursor-pointer gap-3" @click="share.toggleRound(round.key)">
          <el-checkbox :model-value="share.isSelected(round.key)" class="pointer-events-none shrink-0" />
          <!-- 分享模式下内容只读，不响应内部交互 -->
          <div
            class="px-4 py-3 rounded-xl pointer-events-none min-w-0 flex-1 select-none group-hover:bg-N900/8"
            :class="{ 'bg-N900/8': share.isSelected(round.key) }"
          >
            <ContentList v-for="message in round.messages" :key="message.id" :content-list="message.content" />
          </div>
        </div>
      </template>

      <template #empty>
        <MkEmpty description="暂无可分享的对话" class="mt-20" />
      </template>
    </ReverseInfiniteScroll>
    <el-divider />
    <footer class="mk-conversation-content p-4 flex-between">
      <div class="flex-align-center gap-3">
        <!-- 全选当前已加载的对话 -->
        <el-checkbox :model-value="isAllSelected" :indeterminate="isIndeterminate" :disabled="!shareRounds.length" @change="handleSelectAll" />
        <span class="text-N600">已选 {{ selectedCount }}/{{ selectedCount }}</span>
      </div>
      <div>
        <!-- 退出分享模式 -->
        <el-button plain @click="share.close()">取消</el-button>
        <!-- 分享已选对话 -->
        <el-button type="primary" :disabled="!selectedCount" :loading="share.sharing.value" @click="handleShare">分享</el-button>
      </div>
    </footer>
  </main>
</template>
