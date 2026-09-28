<script setup lang="ts">
import { relativeTimeFormat } from '@/utils/time'
import type { Conversation } from '../../core/types'
import { useConversationListStore } from './index'
import AccountMenu from './AccountMenu.vue'

defineOptions({ name: 'ConversationList' })

const { appInfo, conversations, currentChatId, selectConversation, newConversation, deleteChat, toggleLeftSide } = useConversationListStore()

// 历史时间优先使用更新时间，缺少时间的记录不显示占位文案。
const conversationTime = (conversation: Conversation) => relativeTimeFormat(conversation.update_time || conversation.create_time)
</script>

<template>
  <div class="flex-column h-full overflow-hidden p-4">
    <!-- 应用信息与收起侧栏 -->
    <div class="mb-4 flex-between shrink-0 gap-2">
      <div class="min-w-0 flex-align-center gap-2">
        <ApplicationIcon :icon="appInfo?.icon" :size="24" class="shrink-0" />
        <h4 class="truncate" :title="appInfo?.name || 'AI 助手'">{{ appInfo?.name || 'AI 助手' }}</h4>
      </div>
      <!-- 收起左侧 -->
      <el-button text @click="toggleLeftSide()">
        <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
      </el-button>
    </div>

    <!-- 新建对话 -->
    <MkListItem @click="newConversation()">
      <MkIcon name="icon_new-chat_outlined" :size="18" class="mr-2" />
      <span>新建对话</span>
    </MkListItem>
    <div class="flex-between pl-2 mt-4">
      <div class="text-N600 font-medium">历史对话</div>

      <!-- // TODO: 全部清空对话 -->
      <el-button text>
        <MkIcon name="icon_delete-trash_outlined" />
      </el-button>
    </div>

    <!-- 历史列表独立滚动，应用信息和新建入口保持固定。 -->
    <el-scrollbar class="min-h-0 flex-1 mt-1">
      <div v-if="conversations.length === 0" class="text-N600 text-center mt-4">暂无历史记录</div>
      <div v-else class="space-y-1">
        <template v-for="conversation in conversations" :key="conversation.id">
          <MkListItem
            :active="currentChatId === conversation.id"
            :class="{ 'bg-white! text-N900! hover:bg-white!': currentChatId === conversation.id }"
            @click="selectConversation(conversation.id)"
          >
            <template #default>
              <span class="min-w-0 flex-1 truncate" :title="conversation.abstract || '新对话'">
                {{ conversation.abstract || '新对话' }}
              </span>

              <!-- 悬停或聚焦列表行时隐藏时间，显示内置更多操作。 -->
              <span class="-mr-6 shrink-0 text-sm font-normal text-N500 group-hover:invisible group-focus-within:invisible">
                {{ conversationTime(conversation) }}
              </span>
            </template>
            <template #action-dropdown>
              <MkDropdownItem divided @click="deleteChat(conversation.id)">
                <template #icon><MkIcon name="icon_info_outlined" /></template>
                <span>删除</span>
              </MkDropdownItem>
            </template>
          </MkListItem>
        </template>
      </div>
    </el-scrollbar>
    <!-- 账户入口固定在侧栏底部，不随历史列表滚动。 -->
    <div class="mt-3 shrink-0">
      <AccountMenu />
    </div>
  </div>
</template>
