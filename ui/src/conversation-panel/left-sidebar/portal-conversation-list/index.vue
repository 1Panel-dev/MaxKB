<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Conversation } from '../../core/types'
import type { PortalApplicationGroup } from './index'
import { useMessageListStore } from '../../components/message-list/index'
import RenameConversation from '../../components/rename/index.vue'
import { useShowShare } from '../../view/index'
import AccountMenu from '../account-menu/index.vue'
import { useConversationListStore } from '../conversation-list/index'
import HistoryConversationDrawer from './HistoryConversationDrawer.vue'
import { usePortalConversationListStore } from './index'
import { useStore } from '@/stores/chat'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { relativeTimeFormat } from '@/utils/time'

defineOptions({ name: 'PortalConversationList' })

const { t } = useI18n({ useScope: 'global' })

// 门户名称和 Logo 使用认证配置，配置未加载时保留默认展示。
const { auth: authStore } = useStore()
const portalName = computed(() => {
  const meta = authStore.authProfile?.meta
  const name = meta && typeof meta === 'object' && 'portal_name' in meta ? meta.portal_name : undefined
  return typeof name === 'string' && name ? name : t('portal.name.default')
})
const portalLogo = computed(() => authStore.authProfile?.logo)

const msgs = useMessageListStore()
const canShare = computed(() => msgs.messages.value.length > 0 && !msgs.streamLoading.value && !msgs.loading.value)
const showShare = useShowShare()
const portalList = usePortalConversationListStore()
const { applicationGroups, initialLoading, currentApplicationId, isApplicationListActive, toggleGroup } = portalList
const { conversations, currentChatId, selectConversation, deleteChat, newConversation, switchShared, toggleLeftSide } = useConversationListStore()

const historyApplicationId = ref('')
const historyVisible = ref(false)
const handleOpenHistory = (group: PortalApplicationGroup) => {
  historyApplicationId.value = group.id
  historyVisible.value = true
}

// 总数超过 20 条时，每个智能体最多展示最近 5 条会话
const RECENT_CONVERSATION_LIMIT = 5

const isCurrentApplication = (group: PortalApplicationGroup) => group.id === currentApplicationId.value

const groupConversationCount = (group: PortalApplicationGroup) =>
  group.show_history === false ? 0 : Math.max(group.count, isCurrentApplication(group) ? conversations.value.length : group.conversations.length)

// 关闭“显示历史记录”只影响会话展示，智能体本身仍保留在门户侧栏。
const historyEnabledGroups = computed(() => applicationGroups.value.filter((group) => group.show_history !== false))

// 所有智能体的对话总数超过 20 条时，才显示分组的查看更多入口。
const totalConversationCount = computed(() => historyEnabledGroups.value.reduce((total, group) => total + groupConversationCount(group), 0))

// 当前智能体以会话列表 Store 为准；无需查看更多时展示全部已加载会话。
const groupConversations = (group: PortalApplicationGroup) => {
  if (group.show_history === false) return []
  const applicationConversations = isCurrentApplication(group) ? conversations.value : group.conversations
  return totalConversationCount.value > 20 ? applicationConversations.slice(0, RECENT_CONVERSATION_LIMIT) : applicationConversations
}

// 关闭历史记录的智能体仍展示分组；开启历史记录的智能体仅在存在会话时展示。
const historyApplicationGroups = computed(() =>
  applicationGroups.value.filter((group) => group.show_history === false || groupConversations(group).length > 0),
)

const clearableApplicationGroups = computed(() => historyEnabledGroups.value.filter((group) => groupConversations(group).length > 0))

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
  MsgConfirm(t('chat.history.clearTitle'), t('portal.clearAllDescription'), { confirmButtonText: t('common.actions.clear') })
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
        .then(() => MsgSuccess(t('common.messages.clearSuccess')))
    })
    .catch(() => {})
    .finally(() => {
      clearing.value = false
    })
}

// 清空指定智能体的全部历史对话；若为当前智能体，同步清空会话列表并新建对话。
const clearGroupConversationLoading = ref(false)
const handleClearGroupConversations = (group: PortalApplicationGroup) => {
  if (clearGroupConversationLoading.value) return
  clearGroupConversationLoading.value = true
  MsgConfirm(t('portal.clearApplicationTitle'), t('chat.history.clearDescription'), { confirmButtonText: t('common.actions.clear') })
    .then(() =>
      portalList.clearGroupConversations(group.id, () => {
        if (group.id === currentApplicationId.value) {
          conversations.value = []
          switchShared(false)
          newConversation()
        }
      }),
    )
    .then(() => MsgSuccess(t('common.messages.clearSuccess')))
    .catch(() => {})
    .finally(() => {
      clearGroupConversationLoading.value = false
    })
}
</script>

<template>
  <div class="flex-column h-full overflow-hidden p-4">
    <!-- 门户名称与收起侧栏 -->
    <div class="mb-4 flex-between shrink-0 gap-2">
      <div class="min-w-0 flex-align-center gap-2">
        <PortalIcon :icon="portalLogo" />
        <h4 class="truncate">{{ portalName }}</h4>
      </div>
      <!-- 收起左侧 -->
      <MkTooltip :content="t('chat.actions.collapseSidebar')">
        <el-button text @click="toggleLeftSide()">
          <MkIcon name="icon_sidebar_outlined" :size="18" class="text-N900!" />
        </el-button>
      </MkTooltip>
    </div>

    <!-- 全部智能体 -->
    <MkListItem :active="isApplicationListActive" @click="portalList.openApplicationList()">
      <MkIcon :name="isApplicationListActive ? 'icon_card_filled' : 'icon_card_outlined'" :size="18" class="mr-2" />
      <span>{{ t('application.title') }}</span>
    </MkListItem>
    <!-- 新建对话 -->
    <MkTooltip :content="t('chat.newChat')">
      <MkListItem @click="portalList.newConversation()">
        <MkIcon name="icon_new-chat_outlined" :size="18" class="mr-2" />
        <span>{{ t('chat.newChat') }}</span>
      </MkListItem>
    </MkTooltip>
    <div class="flex-between pl-2 mt-4">
      <h6 class="text-N600 font-medium">{{ t('chat.history.label') }}</h6>

      <MkTooltip :content="t('common.actions.clear')">
        <!-- 清空所有智能体的历史对话 -->
        <el-button text :loading="clearing" :disabled="!clearableApplicationGroups.length" @click="handleClearConversations">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </MkTooltip>
    </div>

    <!-- 历史列表独立滚动，门户入口和新建入口保持固定。 -->
    <el-scrollbar class="min-h-0 flex-1 mt-1 -mr-4" view-class="pr-4">
      <el-skeleton v-if="initialLoading" animated />
      <div v-else-if="historyApplicationGroups.length === 0" class="text-N600 text-center mt-4">{{ t('chat.history.empty') }}</div>
      <div v-else class="space-y-1">
        <template v-for="group in historyApplicationGroups" :key="group.id">
          <MkCollapse
            :expanded="group.show_history !== false && group.expanded"
            trigger="header"
            trigger-class="group rounded-md p-2 hover:bg-N900/10 mb-1"
            indicator-position="after"
            @update:expanded="toggleGroup(group.id)"
          >
            <template #indicator="{ expanded }">
              <MkIcon
                v-if="group.show_history !== false"
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
                        <span>{{ t('chat.newChat') }}</span>
                      </MkDropdownItem>
                      <!-- 删除智能体历史分组，待接入对应接口 -->
                      <MkDropdownItem v-if="group.show_history !== false" divided @click="handleClearGroupConversations(group)">
                        <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                        <span>{{ t('portal.clearConversations') }}</span>
                      </MkDropdownItem>
                    </MkDropdownMenu>
                  </template>
                </MkDropdown>
              </div>
            </template>

            <div class="space-y-1" v-if="group.show_history !== false && group.expanded">
              <MkListItem
                v-for="conversation in groupConversations(group)"
                :key="conversation.id"
                :active="isActiveConversation(group, conversation)"
                class="pl-8!"
                @click="handleSelectConversation(group, conversation)"
              >
                <template #default="{ active }">
                  <span class="min-w-0 flex-1 truncate" :title="conversation.abstract || t('chat.defaultConversationTitle')">
                    {{ conversation.abstract || t('chat.defaultConversationTitle') }}
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
                        <!-- 激活所选对话并全选分享 -->
                        <MkDropdownItem
                          v-if="isCurrentApplication(group) && showShare"
                          :disabled="msgs.loading.value || (isActiveConversation(group, conversation) && !canShare)"
                          @click="portalList.shareConversation(group.id, conversation.id)"
                        >
                          <template #icon><MkIcon name="icon_share_outlined" /></template>
                          <span>{{ t('chat.share.label') }}</span>
                        </MkDropdownItem>
                        <RenameConversation :conversation="conversation" :application-id="group.id" @renamed="conversation.abstract = $event" />
                        <!-- 删除历史对话 -->
                        <MkDropdownItem divided @click="handleDeleteConversation(group, conversation)">
                          <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                          <span>{{ t('common.actions.delete') }}</span>
                        </MkDropdownItem>
                      </MkDropdownMenu>
                    </template>
                  </MkDropdown>
                </template>
              </MkListItem>
              <!-- 总数超过 20 条且当前智能体超过 5 条时查看更多 -->
              <MkListItem
                class="pl-8!"
                v-if="totalConversationCount > 20 && groupConversationCount(group) > RECENT_CONVERSATION_LIMIT"
                @click="handleOpenHistory(group)"
              >
                <template #default>
                  <span>{{ t('chat.history.viewMore') }}</span>
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
