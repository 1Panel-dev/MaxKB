<script setup lang="ts">
import { computed, ref } from 'vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { relativeTimeFormat } from '@/utils/time'
import type { Conversation } from '../../core/types'
import { useConversationListStore } from '../conversation-list/index'
import HistoryConversationDrawer from './HistoryConversationDrawer.vue'
import AccountMenu from '../account-menu/index.vue'
import { usePortalConversationListStore, type PortalApplicationGroup } from './index'
import RenameConversation from '../../components/rename/index.vue'

defineOptions({ name: 'PortalConversationList' })

const portalList = usePortalConversationListStore()
const { applicationGroups, currentApplicationId, isApplicationListActive, toggleGroup } = portalList
const { conversations, currentChatId, selectConversation, deleteChat, newConversation, switchShared, toggleLeftSide } = useConversationListStore()

const historyApplicationId = ref('')
const historyVisible = ref(false)
const handleOpenHistory = (group: PortalApplicationGroup) => {
  historyApplicationId.value = group.id
  historyVisible.value = true
}

// 每个智能体最多展示最近 5 条会话
const RECENT_CONVERSATION_LIMIT = 5

const isCurrentApplication = (group: PortalApplicationGroup) => group.id === currentApplicationId.value

// 当前智能体以会话列表 Store 为准，其他智能体使用分组接口返回的会话
const groupConversations = (group: PortalApplicationGroup) =>
  (isCurrentApplication(group) ? conversations.value : group.conversations).slice(0, RECENT_CONVERSATION_LIMIT)

const groupConversationCount = (group: PortalApplicationGroup) =>
  Math.max(group.count, isCurrentApplication(group) ? conversations.value.length : group.conversations.length)

// 仅展示有历史记录的智能体，随当前会话的新建、删除同步更新。
const historyApplicationGroups = computed(() => applicationGroups.value.filter((group) => groupConversations(group).length > 0))

const isActiveConversation = (group: PortalApplicationGroup, conversation: Conversation) =>
  isCurrentApplication(group) && currentChatId.value === conversation.id

const conversationTime = (conversation: Conversation) => relativeTimeFormat(conversation.update_time || conversation.create_time)

const handleSelectConversation = (group: PortalApplicationGroup, conversation: Conversation) => {
  if (isCurrentApplication(group)) selectConversation(conversation.id)
  else portalList.openConversation(group.id, conversation.id)
}

const handleDeleteConversation = (group: PortalApplicationGroup, conversation: Conversation) => {
  if (isCurrentApplication(group)) return deleteChat(conversation.id).then(() => portalList.loadApplicationGroups())
  else portalList.deleteGroupConversation(group.id, conversation.id)
}
// 清空所有智能体的历史，删除成功后同步当前会话；失败时保留尚未删除的记录。
const clearing = ref(false)
const handleClearConversations = () => {
  if (clearing.value) return
  clearing.value = true
  MsgConfirm('确认清空全部历史对话？', '将清空所有智能体的历史对话，清空后无法恢复。', { confirmButtonText: '清空' })
    .then(() => {
      historyVisible.value = false
      return portalList
        .clearConversations((applicationId, chatId) => {
          if (applicationId !== currentApplicationId.value) return
          conversations.value = conversations.value.filter((conversation) => conversation.id !== chatId)
          if (currentChatId.value === chatId) {
            switchShared(false)
            newConversation()
          }
        })
        .then(() => MsgSuccess('清空成功'))
    })
    .catch(() => {})
    .finally(() => {
      clearing.value = false
    })
}
</script>

<template>
  <div class="flex-column h-full overflow-hidden p-4">
    <!-- 门户名称与收起侧栏 -->
    <div class="mb-4 flex-between shrink-0 gap-2">
      <div class="min-w-0 flex-align-center gap-2">
        <PortalIcon />
        <h4 class="truncate">智能体门户</h4>
      </div>
      <!-- 收起左侧 -->
      <MkTooltip content="收起侧边栏">
        <el-button text @click="toggleLeftSide()">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </div>

    <!-- 全部智能体 -->
    <MkListItem :active="isApplicationListActive" @click="portalList.openApplicationList()">
      <MkIcon :name="isApplicationListActive ? 'icon_card_filled' : 'icon_card_outlined'" :size="18" class="mr-2" />
      <span>智能体</span>
    </MkListItem>
    <!-- 新建对话 -->
    <MkTooltip content="新建对话">
      <MkListItem @click="portalList.newConversation()">
        <MkIcon name="icon_new-chat_outlined" :size="18" class="mr-2" />
        <span>新建对话</span>
      </MkListItem>
    </MkTooltip>
    <div class="flex-between pl-2 mt-4">
      <h6 class="text-N600 font-medium">历史对话</h6>

      <MkTooltip content="清空">
        <!-- 清空所有智能体的历史对话 -->
        <el-button text :loading="clearing" :disabled="!historyApplicationGroups.length" @click="handleClearConversations">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </MkTooltip>
    </div>

    <!-- 历史列表独立滚动，门户入口和新建入口保持固定。 -->
    <el-scrollbar :inert="clearing" class="min-h-0 flex-1 mt-1 -mr-4" view-class="pr-4">
      <div v-if="historyApplicationGroups.length === 0" class="text-N600 text-center mt-4">暂无历史记录</div>
      <div v-else class="space-y-1">
        <template v-for="group in historyApplicationGroups" :key="group.id">
          <MkCollapse
            :expanded="group.expanded"
            trigger="header"
            trigger-class="group rounded-md p-2 hover:bg-N900/10 mb-1"
            indicator-position="after"
            @update:expanded="toggleGroup(group.id)"
          >
            <template #indicator="{ expanded }">
              <MkIcon
                name="icon_right_outlined"
                :size="12"
                class="transition-transform text-N600! group-hover:text-N900!"
                :class="{ 'rotate-90': expanded }"
              />
            </template>
            <template #label>
              <!-- 选中智能体，进入其新建对话 -->
              <div class="min-w-0 flex-align-center gap-2">
                <ApplicationIcon :icon="group.icon" :size="18" class="shrink-0" />
                <span class="min-w-0 truncate" :title="group.name">{{ group.name }}</span>
              </div>
              <!-- 智能体分组操作，与单条会话的操作独立 -->
              <div class="order-last ml-auto shrink-0 font-normal text-N900" @click.stop @keydown.stop>
                <MkDropdown trigger="click" :teleported="false">
                  <el-button text>
                    <MkIcon name="icon_more_outlined" />
                  </el-button>
                  <template #dropdown>
                    <MkDropdownMenu>
                      <!-- 新建当前分组智能体的对话 -->
                      <MkDropdownItem @click="portalList.openApplication(group.id)">
                        <template #icon><MkIcon name="icon_new-chat_outlined" /></template>
                        <span>新建对话</span>
                      </MkDropdownItem>
                      <!-- 删除智能体历史分组，待接入对应接口 -->
                      <MkDropdownItem divided disabled>
                        <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                        <span>删除</span>
                      </MkDropdownItem>
                    </MkDropdownMenu>
                  </template>
                </MkDropdown>
              </div>
            </template>

            <div class="space-y-1" v-if="group.expanded">
              <MkListItem
                v-for="conversation in groupConversations(group)"
                :key="conversation.id"
                :active="isActiveConversation(group, conversation)"
                class="pl-8!"
                @click="handleSelectConversation(group, conversation)"
              >
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
                  <MkDropdown trigger="click" persistent :teleported="false">
                    <!-- 打开历史对话操作菜单 -->
                    <el-button text><MkIcon name="icon_more_outlined" /></el-button>
                    <template #dropdown>
                      <MkDropdownMenu>
                        <RenameConversation :conversation="conversation" :application-id="group.id" @renamed="conversation.abstract = $event" />
                        <!-- 删除历史对话 -->
                        <MkDropdownItem divided @click="handleDeleteConversation(group, conversation)">
                          <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                          <span>删除</span>
                        </MkDropdownItem>
                      </MkDropdownMenu>
                    </template>
                  </MkDropdown>
                </template>
              </MkListItem>
              <!-- 超过5条 查看更多 -->
              <MkListItem class="pl-8!" v-if="groupConversationCount(group) > RECENT_CONVERSATION_LIMIT" @click="handleOpenHistory(group)">
                <template #default>
                  <span>查看更多</span>
                  <span>
                    ({{
                      groupConversationCount(group) - RECENT_CONVERSATION_LIMIT > 99
                        ? '99+'
                        : groupConversationCount(group) - RECENT_CONVERSATION_LIMIT
                    }})
                  </span>
                </template>
              </MkListItem>
            </div>
          </MkCollapse>
        </template>
      </div>
    </el-scrollbar>
    <HistoryConversationDrawer
      v-if="historyApplicationId"
      v-model="historyVisible"
      :application-id="historyApplicationId"
      @closed="historyApplicationId = ''"
    />
    <!-- 账户入口固定在侧栏底部，不随历史列表滚动。 -->
    <div class="mt-3 shrink-0">
      <AccountMenu />
    </div>
  </div>
</template>
