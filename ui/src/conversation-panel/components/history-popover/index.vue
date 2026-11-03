<script setup lang="ts">
import { ref } from 'vue'
import { ElMessageBox, type ScrollbarDirection } from 'element-plus'
import type { Conversation } from '../../core/types'
import { useConversationListStore } from '../../left-sidebar/conversation-list/index'
import { relativeTimeFormat } from '@/utils/time'
import { MsgConfirm } from '@/utils/message'

defineOptions({ name: 'HistoryPopover' })

const conversationList = useConversationListStore()
const visible = ref(false)
const clearing = ref(false)

// 每次打开重新加载第一页，滚动到底部时续载。
const handleShow = () => conversationList.loadConversations()
const handleEndReached = (direction: ScrollbarDirection) => {
  if (direction === 'bottom') void conversationList.loadMore()
}

// 历史时间优先使用更新时间，缺少时间的记录不显示占位文案。
const conversationTime = (conversation: Conversation) => relativeTimeFormat(conversation.update_time || conversation.create_time)

/* 切换会话后收起浮层。 */
function handleSelectConversation(conversation: Conversation) {
  conversationList.selectConversation(conversation.id)
  visible.value = false
}

/* 重命名：去除首尾空格后提交，取消或请求失败保留原名称。 */
function handleRenameConversation(conversation: Conversation) {
  ElMessageBox.prompt('', '重命名', {
    inputValue: conversation.abstract || '',
    inputPattern: /\S/,
    inputErrorMessage: '请输入对话名称',
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => conversationList.renameChat(conversation.id, value.trim()))
    .catch(() => {})
}

function handleDeleteConversation(conversation: Conversation) {
  MsgConfirm('确认删除该对话？', '删除后无法恢复。')
    .then(() => conversationList.deleteChat(conversation.id))
    .catch(() => {})
}

/*
 * 批量清空：会话接口未提供批量删除，先加载全部分页，切到新对话后逐条删除；
 * 中途失败时保留未删除的记录。
 */
function handleClearConversations() {
  if (clearing.value) return
  MsgConfirm('确认清空全部历史对话？', '清空后无法恢复。', { confirmButtonText: '清空' })
    .then(async () => {
      clearing.value = true
      while (conversationList.hasMore.value) await conversationList.loadMore()
      conversationList.newConversation()
      for (const { id } of [...conversationList.conversations.value]) await conversationList.deleteChat(id)
    })
    .catch(() => {})
    .finally(() => {
      clearing.value = false
    })
}
</script>

<template>
  <el-popover v-model:visible="visible" trigger="click" placement="bottom-end" :width="280" popper-class="p-2!" @show="handleShow">
    <template #reference>
      <span class="inline-flex">
        <MkTooltip content="历史对话">
          <!-- 打开历史对话 -->
          <el-button text>
            <MkIcon name="icon_history_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </span>
    </template>
    <div class="flex-between pl-2">
      <h6 class="text-N600">历史对话</h6>
      <MkTooltip content="清空">
        <!-- 批量清空历史对话 -->
        <el-button text :loading="clearing" :disabled="!conversationList.conversations.value.length" @click="handleClearConversations">
          <MkIcon name="icon_delete-trash_outlined" />
        </el-button>
      </MkTooltip>
    </div>
    <el-scrollbar max-height="360px" class="mt-1" @end-reached="handleEndReached">
      <div v-if="!conversationList.conversations.value.length" class="py-4 text-center text-N600">暂无历史记录</div>
      <div v-else class="space-y-1">
        <!-- 切换历史对话 -->
        <MkListItem
          v-for="conversation in conversationList.conversations.value"
          :key="conversation.id"
          :active="conversationList.currentChatId.value === conversation.id"
          @click="handleSelectConversation(conversation)"
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
          <template #action-dropdown>
            <!-- 重命名历史对话 -->
            <MkDropdownItem @click="handleRenameConversation(conversation)">
              <template #icon><MkIcon name="icon_edit_outlined" /></template>
              <span>重命名</span>
            </MkDropdownItem>
            <!-- 删除历史对话 -->
            <MkDropdownItem @click="handleDeleteConversation(conversation)">
              <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
              <span>删除</span>
            </MkDropdownItem>
          </template>
        </MkListItem>
      </div>
    </el-scrollbar>
  </el-popover>
</template>
