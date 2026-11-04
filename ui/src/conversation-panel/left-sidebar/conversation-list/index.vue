<script setup lang="ts">
import { ref } from 'vue'
import { MsgConfirm } from '@/utils/message'
import RenameConversation from '../../components/rename/index.vue'
import { relativeTimeFormat } from '@/utils/time'
import type { Conversation } from '../../core/types'
import { useConversationListStore } from './index'
import AccountMenu from '../account-menu/index.vue'

defineOptions({ name: 'ConversationList' })

const { appInfo, conversations, currentChatId, selectConversation, newConversation, deleteChat, toggleLeftSide, hasMore, loadMore } =
  useConversationListStore()

// 历史时间优先使用更新时间，缺少时间的记录不显示占位文案。
const conversationTime = (conversation: Conversation) => relativeTimeFormat(conversation.update_time || conversation.create_time)
// 会话维护沿用调试历史记录的确认与请求流程。
const clearing = ref(false)

function handleDeleteConversation(conversation: Conversation) {
  MsgConfirm('确认删除该对话？', '删除后无法恢复。')
    .then(() => deleteChat(conversation.id))
    .catch(() => {})
}

// 先加载全部分页，再切到新对话并逐条删除；失败时保留未删除记录。
function handleClearConversations() {
  if (clearing.value) return
  MsgConfirm('确认清空全部历史对话？', '清空后无法恢复。', { confirmButtonText: '清空' })
    .then(async () => {
      clearing.value = true
      while (hasMore.value) await loadMore()
      newConversation()
      for (const { id } of [...conversations.value]) await deleteChat(id)
    })
    .catch(() => {})
    .finally(() => {
      clearing.value = false
    })
}
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
      <MkTooltip content="收起侧边栏">
        <el-button text @click="toggleLeftSide()" class="-mr-1">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </div>

    <!-- 新建对话 -->
    <MkTooltip content="新建对话">
      <MkListItem @click="newConversation()">
        <MkIcon name="icon_new-chat_outlined" :size="18" class="mr-2" />
        <span>新建对话</span>
      </MkListItem>
    </MkTooltip>
    <div class="flex-between pl-2 mt-4">
      <h6 class="text-N600">历史对话</h6>

      <MkTooltip content="清空">
        <!-- 批量清空历史对话 -->
        <el-button text :loading="clearing" :disabled="!conversations.length" @click="handleClearConversations">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </MkTooltip>
    </div>

    <!-- 历史列表独立滚动，应用信息和新建入口保持固定。 -->
    <el-scrollbar class="min-h-0 flex-1 mt-1 -mr-4" view-class="pr-4">
      <div v-if="conversations.length === 0" class="text-N600 text-center mt-4">暂无历史记录</div>
      <div v-else class="space-y-1">
        <template v-for="conversation in conversations" :key="conversation.id">
          <MkListItem :active="currentChatId === conversation.id" @click="selectConversation(conversation.id)">
            <template #default="{ active }">
              <span class="min-w-0 flex-1 truncate" :title="conversation.abstract || '新对话'">
                {{ conversation.abstract || '新对话' }}
              </span>

              <!-- 选中、悬停或聚焦列表行时隐藏时间，显示内置更多操作。 -->
              <span
                class="-mr-6 shrink-0 text-sm font-normal text-N500 group-hover:invisible group-focus-within:invisible"
                :class="{ invisible: active }"
              >
                {{ conversationTime(conversation) }}
              </span>
            </template>
            <template #action>
              <MkDropdown trigger="click" persistent>
                <!-- 打开历史对话操作菜单 -->
                <el-button text><MkIcon name="icon_more_outlined" /></el-button>
                <template #dropdown>
                  <MkDropdownMenu>
                    <!-- 重命名 -->
                    <RenameConversation :conversation="conversation" />
                    <!-- 删除历史对话 -->
                    <MkDropdownItem divided @click="handleDeleteConversation(conversation)">
                      <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                      <span>删除</span>
                    </MkDropdownItem>
                  </MkDropdownMenu>
                </template>
              </MkDropdown>
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
