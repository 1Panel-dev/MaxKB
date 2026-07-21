<template>
  <aside class="sidebar" :class="[mode, { open }]">
    <div class="sidebar-header">
      <span class="sidebar-title">对话历史</span>
    </div>

    <div class="sidebar-nav">
      <div v-if="conversations.length === 0" class="nav-empty">暂无对话</div>
      <div
        v-for="item in conversations"
        :key="item.id"
        class="nav-item"
        :class="{ active: currentId === item.id }"
        @click="handleSwitch(item.id)"
      >
        <span class="nav-item-text">{{ item.name || '新对话' }}</span>
        <span class="nav-item-actions">
          <button @click.stop="startRename(item)">重命名</button>
          <button class="delete" @click.stop="handleDelete(item.id)">删除</button>
        </span>
      </div>
    </div>

    <div class="sidebar-footer">
      <button @click="handleNew">
        <span>+</span> 新对话
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const props = defineProps<{
  open: boolean
  mode: 'push' | 'drawer'
  conversations: any[]
  currentId: string
}>()

const emit = defineEmits<{
  'update:open': [val: boolean]
  'update:mode': [val: 'push' | 'drawer']
  switch: [id: string]
  delete: [id: string]
  rename: [id: string, name: string]
  new: []
}>()

const renamingId = ref<string | null>(null)
const renameValue = ref('')

const handleSwitch = (id: string) => {
  emit('switch', id)
  if (props.mode === 'drawer') emit('update:open', false)
}

const handleDelete = (id: string) => {
  emit('delete', id)
}

const handleNew = () => {
  emit('new')
}

const toggleMode = () => {
  emit('update:mode', props.mode === 'push' ? 'drawer' : 'push')
}

const startRename = (item: any) => {
  renamingId.value = item.id
  renameValue.value = item.name || ''
  nextTick(() => {
    const input = document.querySelector('.rename-input') as HTMLInputElement
    input?.focus()
    input?.select()
  })
}

const confirmRename = () => {
  if (renamingId.value) {
    emit('rename', renamingId.value, renameValue.value)
  }
  renamingId.value = null
}
</script>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg2, #fafafa);
  border-right: 1px solid var(--bd, #dcdfe6);
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar.push {
  position: relative;
  z-index: 1;
  width: 0;
  min-width: 0;
  border-right-width: 0;
  pointer-events: none;
  transition:
    width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    min-width 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    border-right-width 0.25s;
}

.sidebar.push.open {
  width: 260px;
  min-width: 260px;
  border-right-width: 1px;
  pointer-events: auto;
}

.sidebar.drawer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 260px;
  z-index: 40;
  transform: translateX(-100%);
  transition:
    transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 0.25s;
}

.sidebar.drawer.open {
  transform: translateX(0);
  box-shadow: 4px 0 16px rgba(0, 0, 0, 0.2);
}

.sidebar-header {
  display: flex;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid var(--bd, #dcdfe6);
}

.sidebar-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--t1, #303133);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.nav-empty {
  font-size: 12px;
  color: var(--t3, #909399);
  text-align: center;
  padding: 20px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.15s;
}

.nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.nav-item.active {
  background: rgba(0, 0, 0, 0.06);
}

.nav-item-text {
  flex: 1;
  min-width: 0;
  font-size: 13px;
  color: var(--t2, #606266);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item.active .nav-item-text {
  color: var(--t1, #303133);
  font-weight: 500;
}

.nav-item-actions {
  display: none;
  gap: 2px;
  flex-shrink: 0;
}

.nav-item:hover .nav-item-actions,
.nav-item.active .nav-item-actions {
  display: flex;
}

.nav-item-actions button {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--t3, #909399);
  cursor: pointer;
  font-size: 11px;
  transition: background 0.12s, color 0.12s;
}

.nav-item-actions button:hover {
  background: rgba(0, 0, 0, 0.06);
  color: var(--t2, #606266);
}

.nav-item-actions button.delete:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.sidebar-footer {
  padding: 8px;
  border-top: 1px solid var(--bd, #dcdfe6);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sidebar-footer button {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--t3, #909399);
  font-size: 13px;
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  transition: background 0.12s, color 0.12s;
}

.sidebar-footer button:hover {
  background: rgba(0, 0, 0, 0.04);
  color: var(--t2, #606266);
}
</style>
