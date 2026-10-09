<script setup lang="ts">
import { relativeTimeFormat } from '@/utils/time'
import type { Conversation } from '../../core/types'
import { useConversationListStore } from '../conversation-list/index'
import AccountMenu from '../conversation-list/AccountMenu.vue'
import { usePortalConversationListStore, type PortalApplicationGroup } from './index'

defineOptions({ name: 'PortalConversationList' })

const portalList = usePortalConversationListStore()
const { applicationGroups, currentApplicationId, isApplicationListActive, toggleGroup } = portalList
const { conversations, currentChatId, selectConversation, deleteChat, toggleLeftSide } = useConversationListStore()

// 每个智能体最多展示最近 5 条会话
const RECENT_CONVERSATION_LIMIT = 5

const isCurrentApplication = (group: PortalApplicationGroup) => group.id === currentApplicationId.value

// 当前智能体以会话列表 Store 为准，其他智能体使用分组接口返回的会话
const groupConversations = (group: PortalApplicationGroup) =>
  (isCurrentApplication(group) ? conversations.value : group.conversations).slice(0, RECENT_CONVERSATION_LIMIT)

// 当前智能体的新建对话（没有选中会话）时，选中智能体本身
const isActiveApplication = (group: PortalApplicationGroup) => isCurrentApplication(group) && !currentChatId.value

// 选中智能体进入其新建对话，并展开其会话；进入后会话以会话列表 Store 为准，无需查询分组会话
const handleSelectApplication = (group: PortalApplicationGroup) => {
  group.expanded = true
  portalList.openApplication(group.id)
}

const isActiveConversation = (group: PortalApplicationGroup, conversation: Conversation) =>
  isCurrentApplication(group) && currentChatId.value === conversation.id

const conversationTime = (conversation: Conversation) => relativeTimeFormat(conversation.update_time || conversation.create_time)

const handleSelectConversation = (group: PortalApplicationGroup, conversation: Conversation) => {
  if (isCurrentApplication(group)) selectConversation(conversation.id)
  else portalList.openConversation(group.id, conversation.id)
}

const handleDeleteConversation = (group: PortalApplicationGroup, conversation: Conversation) => {
  if (isCurrentApplication(group)) deleteChat(conversation.id)
  else portalList.deleteGroupConversation(group.id, conversation.id)
}
</script>

<template>
  <div class="flex-column h-full overflow-hidden p-4">
    <!-- 门户名称与收起侧栏 -->
    <div class="mb-4 flex-between shrink-0 gap-2">
      <div class="min-w-0 flex-align-center gap-2">
        <MkIcon name="icon_application-shop_filled" :size="20" class="shrink-0 text-primary" />
        <h4 class="truncate">智能体门户</h4>
      </div>
      <!-- 收起左侧 -->
      <el-button text @click="toggleLeftSide()">
        <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
      </el-button>
    </div>

    <!-- 全部智能体 -->
    <MkListItem :active="isApplicationListActive" @click="portalList.openApplicationList()">
      <MkIcon name="icon_all_outlined" :size="18" class="mr-2" />
      <span>全部智能体</span>
    </MkListItem>
    <!-- 新建对话 -->
    <MkListItem @click="portalList.newConversation()">
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

    <!-- 历史列表独立滚动，门户入口和新建入口保持固定。 -->
    <el-scrollbar class="min-h-0 flex-1 mt-1">
      <div v-if="applicationGroups.length === 0" class="text-N600 text-center mt-4">暂无历史记录</div>
      <div v-else class="space-y-1">
        <template v-for="group in applicationGroups" :key="group.id">
          <!-- 选中智能体，进入其新建对话 -->
          <MkListItem
            :active="isActiveApplication(group)"
            :class="{ 'bg-white! text-N900! hover:bg-white!': isActiveApplication(group) }"
            @click="handleSelectApplication(group)"
          >
            <ApplicationIcon :icon="group.icon" :size="18" class="mr-2 shrink-0" />
            <span class="min-w-0 truncate" :title="group.name">{{ group.name }}</span>
            <!-- 展开或收起智能体的会话 -->
            <span class="ml-1 flex-center shrink-0 cursor-pointer" @click.stop="toggleGroup(group.id)">
              <MkIcon :name="group.expanded ? 'icon_down_outlined' : 'icon_right_outlined'" :size="14" class="text-N500" />
            </span>
          </MkListItem>

          <template v-if="group.expanded">
            <MkListItem
              v-for="conversation in groupConversations(group)"
              :key="conversation.id"
              :active="isActiveConversation(group, conversation)"
              class="pl-8!"
              :class="{ 'bg-white! text-N900! hover:bg-white!': isActiveConversation(group, conversation) }"
              @click="handleSelectConversation(group, conversation)"
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
                <!-- 删除 -->
                <MkDropdownItem divided @click="handleDeleteConversation(group, conversation)">
                  <template #icon><MkIcon name="icon_info_outlined" /></template>
                  <span>删除</span>
                </MkDropdownItem>
              </template>
            </MkListItem>
          </template>
        </template>
      </div>
    </el-scrollbar>
    <!-- 账户入口固定在侧栏底部，不随历史列表滚动。 -->
    <div class="mt-3 shrink-0">
      <AccountMenu />
    </div>
  </div>
</template>
