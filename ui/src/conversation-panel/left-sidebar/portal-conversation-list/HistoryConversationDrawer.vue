<script setup lang="ts">
import { ref } from 'vue'
import ConversationApi from '@/api/chat/conversation'
import type { PortalConversationSummary } from '@/api/types'
import { relativeTimeFormat } from '@/utils/time'
import { useConversationListStore } from '../conversation-list/index'
import { usePortalConversationListStore } from './index'
import RenameConversation from '../../components/rename/index.vue'

defineOptions({ name: 'HistoryConversationDrawer' })
const props = defineProps<{ applicationId: string }>()
const visible = defineModel<boolean>({ required: true })
const portalList = usePortalConversationListStore()
const conversationList = useConversationListStore()
const selectedApplicationId = ref(props.applicationId)
const keyword = ref('')
const conversations = ref<PortalConversationSummary[]>([])
const scrollRef = ref<{ reset: () => Promise<void> }>()

// 搜索与切换智能体从第一页重新加载，分页由共享滚动组件维护。
const loadConversations = ({ currentPage, pageSize }: { currentPage: number; pageSize: number }) =>
  ConversationApi.getPortalConversationPage(selectedApplicationId.value, currentPage, pageSize, keyword.value.trim())
const handleSearch = () => scrollRef.value?.reset()
const handleApplicationChange = () => {
  keyword.value = ''
  return scrollRef.value?.reset()
}

// 选择历史后关闭抽屉；当前智能体复用会话切换，其他智能体通过门户导航。
const handleSelectConversation = (conversation: PortalConversationSummary) => {
  if (selectedApplicationId.value === portalList.currentApplicationId.value) conversationList.selectConversation(conversation.id)
  else portalList.openConversation(selectedApplicationId.value, conversation.id)
  visible.value = false
}
const isActiveConversation = (conversation: PortalConversationSummary) =>
  selectedApplicationId.value === portalList.currentApplicationId.value && conversation.id === conversationList.currentChatId.value

// 删除成功后同步侧栏，并重新加载抽屉，补齐当前筛选下的历史。
const handleDeleteConversation = (conversation: PortalConversationSummary) => {
  const applicationId = selectedApplicationId.value
  const request =
    applicationId === portalList.currentApplicationId.value
      ? conversationList.deleteChat(conversation.id)
      : portalList.deleteGroupConversation(applicationId, conversation.id)
  return request.then(() => Promise.all([portalList.loadApplicationGroups(), scrollRef.value?.reset()]))
}
</script>

<template>
  <MkDrawer v-model="visible" title="历史对话" :size="600" :close-on-click-modal="true" :close-on-press-escape="true">
    <div class="mb-4 flex-align-center gap-3">
      <!-- 切换历史对话所属智能体 -->
      <el-select v-model="selectedApplicationId" class="w-50! shrink-0" @change="handleApplicationChange">
        <template #label="{ label }">
          <span class="flex-align-center gap-2">
            <ApplicationIcon :icon="portalList.applicationGroups.value.find((group) => group.id === selectedApplicationId)?.icon" :size="18" />
            <span class="truncate">{{ label }}</span>
          </span>
        </template>
        <el-option v-for="group in portalList.applicationGroups.value" :key="group.id" :label="group.name" :value="group.id">
          <span class="flex-align-center gap-2">
            <ApplicationIcon :icon="group.icon" :size="18" />
            {{ group.name }}
          </span>
        </el-option>
      </el-select>
      <!-- 按历史对话摘要搜索 -->
      <MkSearchInput v-model="keyword" class="min-w-0 flex-1" placeholder="搜索" @change="handleSearch" />
    </div>
    <MkInfiniteScroll ref="scrollRef" v-model="conversations" :load="loadConversations">
      <div class="space-y-1">
        <!-- 打开历史对话 -->
        <MkListItem
          v-for="conversation in conversations"
          :key="conversation.id"
          :active="isActiveConversation(conversation)"
          @click="handleSelectConversation(conversation)"
          class="px-4!"
        >
          <template #default="{ active }">
            <span class="min-w-0 flex-1 truncate" :title="conversation.abstract || '新对话'">{{ conversation.abstract || '新对话' }}</span>
            <span class="-mr-6 shrink-0 text-sm text-N500 group-hover:invisible group-focus-within:invisible" :class="{ invisible: active }">
              {{ relativeTimeFormat(conversation.update_time || conversation.create_time) }}
            </span>
          </template>
          <template #action>
            <MkDropdown trigger="click" persistent :teleported="false">
              <!-- 打开历史对话操作菜单 -->
              <el-button text><MkIcon name="icon_more_outlined" /></el-button>
              <template #dropdown>
                <MkDropdownMenu>
                  <!-- 重命名 -->
                  <RenameConversation
                    :conversation="conversation"
                    :application-id="selectedApplicationId"
                    @renamed="conversation.abstract = $event"
                  />
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
      </div>
      <template #empty><MkEmpty :type="keyword ? 'search' : 'default'" :description="keyword ? '没有匹配的历史对话' : '暂无历史记录'" /></template>
    </MkInfiniteScroll>
  </MkDrawer>
</template>
