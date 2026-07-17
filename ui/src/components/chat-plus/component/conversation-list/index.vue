<template>
  <div class="conversation-list" :class="{ open: isOpen }">
    <div class="conv-header">
      <button class="new-chat-btn" @click="handleNew">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>
        </svg>
        <span>新对话</span>
      </button>
    </div>

    <div class="conv-body">
      <div
        v-for="item in conversations"
        :key="item.id"
        :class="['conv-item', { active: item.id === currentId }]"
        @click="handleOpen(item.id)"
      >
        <div class="conv-item-name">{{ item.name || '新对话' }}</div>
        <div class="conv-item-actions">
          <button class="item-btn" @click.stop="handleRename(item)">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M10 2l2 2-7 7H3v-2l7-7z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <button class="item-btn danger" @click.stop="handleDelete(item.id)">
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M3 4h8M5 4V3a1 1 0 011-1h2a1 1 0 011 1v1M4 4v7a1 1 0 001 1h4a1 1 0 001-1V4" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { chatBus, ChatEvents } from '../../bus'

defineProps<{
  conversations: any[]
  currentId?: string
  isOpen?: boolean
}>()

const handleNew = () => {
  chatBus.emit(ChatEvents.NEW_CONVERSATION)
}

const handleOpen = (id: string) => {
  chatBus.emit(ChatEvents.OPEN_CONVERSATION, id)
}

const handleDelete = (id: string) => {
  chatBus.emit(ChatEvents.DELETE_CONVERSATION, id)
}

const handleRename = (item: any) => {
  const name = prompt('重命名对话', item.name || '')
  if (name !== null && name.trim()) {
    chatBus.emit(ChatEvents.RENAME_CONVERSATION, item.id, name.trim())
  }
}
</script>
