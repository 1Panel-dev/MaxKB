<template>
  <aside class="sidebar">
    <div class="sidebar-content">
      <!-- 应用信息 -->
      <div class="sidebar-header">
        <div class="app-info">
          <el-avatar v-if="appInfo?.icon" shape="square" :size="32" style="background: none">
            <img :src="appInfo.icon" alt="" />
          </el-avatar>
          <div v-else class="app-icon-placeholder">
            <el-icon :size="20"><ChatDotRound /></el-icon>
          </div>
          <h4 class="app-name" :title="appInfo?.name || 'AI 助手'">{{ appInfo?.name || 'AI 助手' }}</h4>
        </div>
        <!-- 收起左侧 -->
        <button class="collapse-btn" @click="toggleLeftSide()">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="1.5" y="2.5" width="13" height="11" rx="2" stroke="currentColor" stroke-width="1.4" />
            <line x1="6" y1="2.5" x2="6" y2="13.5" stroke="currentColor" stroke-width="1.4" />
          </svg>
        </button>
      </div>

      <!-- 新建对话按钮 -->
      <div class="sidebar-action">
        <el-button type="primary" plain class="add-button" @click="newConversation()">
          <el-icon><Plus /></el-icon>
          <span>新建对话</span>
        </el-button>
      </div>

      <div class="sidebar-title"><span>对话历史</span></div>

      <!-- 对话列表 -->
      <div class="sidebar-nav">
        <div v-if="conversations.length === 0" class="nav-empty">
          <el-text type="info">暂无对话</el-text>
        </div>
        <div
          v-for="item in conversations"
          :key="item.id"
          class="nav-item"
          :class="{ active: currentChatId === item.id }"
          @click="selectConversation(item.id)"
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
            <span class="nav-item-text" :title="item.abstract || '新对话'">{{ item.abstract || '新对话' }}</span>
            <div class="nav-item-actions" @click.stop>
              <el-dropdown trigger="click">
                <el-button text class="action-btn"><el-icon><MoreFilled /></el-icon></el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click.stop="startRename(item)">
                      <el-icon><Edit /></el-icon>重命名
                    </el-dropdown-item>
                    <el-dropdown-item @click.stop="deleteChat(item.id)">
                      <el-icon><Delete /></el-icon>删除
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
import { useConversationListStore } from './index'

const {
  appInfo,
  conversations,
  currentChatId,
  selectConversation,
  newConversation,
  deleteChat,
  renameChat,
  toggleLeftSide,
} = useConversationListStore()

const renamingId = ref<string | null>(null)
const renameValue = ref('')

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
  if (renamingId.value) renameChat(renamingId.value, renameValue.value)
  renamingId.value = null
}
</script>

<style scoped lang="scss">
/* 布局(挤压/抽屉/贴边)由 core/layout 负责;此处只作填充容器的纯内容 */
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  width: 100%;
  background: var(--bg2, #fafafa);
  overflow: hidden;
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
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 16px;
}

.app-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.collapse-btn {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: var(--el-text-color-secondary);
}
.collapse-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: var(--el-text-color-primary);
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
</style>
