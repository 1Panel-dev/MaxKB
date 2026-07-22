<template>
  <aside class="sidebar" :class="[mode, { open }]">
    <div class="sidebar-content">
      <!-- 应用信息 -->
      <div class="sidebar-header">
        <div class="app-info">
          <el-avatar
            v-if="store.appInfo.value?.icon"
            shape="square"
            :size="32"
            style="background: none"
          >
            <img :src="store.appInfo.value.icon" alt="" />
          </el-avatar>
          <div v-else class="app-icon-placeholder">
            <el-icon :size="20"><ChatDotRound /></el-icon>
          </div>
          <h4 class="app-name" :title="store.appInfo.value?.name || 'AI 助手'">
            {{ store.appInfo.value?.name || 'AI 助手' }}
          </h4>
        </div>
      </div>

      <!-- 新建对话按钮 -->
      <div class="sidebar-action">
        <el-button type="primary" plain class="add-button" @click="handleNew">
          <el-icon><Plus /></el-icon>
          <span>新建对话</span>
        </el-button>
      </div>

      <!-- 历史记录标题 -->
      <div class="sidebar-title">
        <span>对话历史</span>
      </div>

      <!-- 对话列表 -->
      <div class="sidebar-nav">
        <div v-if="store.conversations.value.length === 0" class="nav-empty">
          <el-text type="info">暂无对话</el-text>
        </div>
        <div
          v-for="item in store.conversations.value"
          :key="item.id"
          class="nav-item"
          :class="{ active: store.currentChatId.value === item.id }"
          @click="handleSwitch(item.id)"
        >
          <template v-if="renamingId === item.id">
            <el-input
              v-model="renameValue"
              size="small"
              class="rename-input"
              @blur="confirmRename"
              @keyup.enter="confirmRename"
              @click.stop
            />
          </template>
          <template v-else>
            <span class="nav-item-text" :title="item.abstract || '新对话'">
              {{ item.abstract || '新对话' }}
            </span>
            <div class="nav-item-actions" @click.stop>
              <el-dropdown trigger="click">
                <el-button text class="action-btn">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click.stop="startRename(item)">
                      <el-icon><Edit /></el-icon>
                      重命名
                    </el-dropdown-item>
                    <el-dropdown-item @click.stop="handleDelete(item.id)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Plus, MoreFilled, Edit, Delete, ChatDotRound } from '@element-plus/icons-vue'
import { useChatStoreByType } from '../common/use-chat-store'
import type { ChatType } from '../common/types'

const props = withDefaults(
  defineProps<{
    type?: ChatType
    open: boolean
    mode: 'push' | 'drawer'
  }>(),
  { type: 'CHAT' },
)

const emit = defineEmits<{
  'update:open': [val: boolean]
  'update:mode': [val: 'push' | 'drawer']
}>()

const store = useChatStoreByType(props.type)

const renamingId = ref<string | null>(null)
const renameValue = ref('')

const handleSwitch = async (id: string) => {
  store.currentChatId.value = id
  await store.loadMessages(id)
  if (props.mode === 'drawer') emit('update:open', false)
}

const handleDelete = async (id: string) => {
  await store.deleteChat(id)
  if (store.currentChatId.value === id) {
    store.currentChatId.value = store.conversations.value[0]?.id || ''
    if (store.currentChatId.value) {
      await store.loadMessages(store.currentChatId.value)
    }
  }
}

const handleNew = async () => {
  const id = await store.openChat(store.applicationId.value)
  store.currentChatId.value = id
  await store.loadConversations()
  await store.loadMessages(id)
}

const toggleMode = () => {
  emit('update:mode', props.mode === 'push' ? 'drawer' : 'push')
}

const startRename = (item: any) => {
  renamingId.value = item.id
  renameValue.value = item.abstract || ''
  nextTick(() => {
    const input = document.querySelector('.rename-input') as HTMLInputElement
    input?.focus()
    input?.select()
  })
}

const confirmRename = () => {
  if (renamingId.value) {
    store.renameChat(renamingId.value, renameValue.value)
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
  width: auto;
  min-width: 200px;
  max-width: 280px;
  border-right-width: 1px;
  pointer-events: auto;
}

.sidebar.drawer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
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

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 16px;
  overflow: hidden;
  box-sizing: border-box;
  max-width: 100%;
}

.sidebar-header {
  margin-bottom: 16px;
}

.app-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-icon-placeholder {
  width: 32px;
  height: 32px;
  border-radius: 4px;
  background: var(--el-color-primary-light-9);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
}

.app-name {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 185px;
}

.sidebar-action {
  margin-bottom: 16px;
}

.add-button {
  width: 100%;
  border: 1px solid var(--el-color-primary-light-5);
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.add-button:hover {
  background-color: var(--el-color-primary-light-8);
  border-color: var(--el-color-primary-light-4);
  color: var(--el-color-primary);
}

:deep(.el-button--primary.is-plain) {
  border-color: var(--el-color-primary-light-5);
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

:deep(.el-button--primary.is-plain:hover) {
  background-color: var(--el-color-primary-light-8);
  border-color: var(--el-color-primary-light-4);
  color: var(--el-color-primary);
}

.sidebar-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 0;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

.nav-empty {
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
  margin-bottom: 2px;
  overflow: hidden;
  box-sizing: border-box;
  max-width: 100%;
}

.nav-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.nav-item.active {
  background: rgba(0, 0, 0, 0.06);
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.nav-item.active:hover {
  background: rgba(0, 0, 0, 0.06);
}

.nav-item-text {
  flex: 1;
  min-width: 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.nav-item.active .nav-item-text {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.nav-item-actions {
  flex-shrink: 0;
  visibility: hidden;
}

.nav-item:hover .nav-item-actions,
.nav-item:focus-within .nav-item-actions {
  visibility: visible;
}

.action-btn {
  padding: 1px !important;
  height: 24px;
  width: 24px;
}

.action-btn .el-icon {
  font-size: 16px;
  color: var(--el-text-color-secondary);
}

.action-btn:hover .el-icon {
  color: var(--el-text-color-primary);
}

.sidebar-footer {
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
