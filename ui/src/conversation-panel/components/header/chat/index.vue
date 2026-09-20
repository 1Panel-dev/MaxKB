<template>
  <header class="panel-header">
    <!-- 左侧收起时才在顶部显示:展开左侧 + 新建对话(展开时它们在侧栏内) -->
    <template v-if="!list.leftSideOpen.value">
      <!-- 展开左侧 -->
      <button class="header-btn" @click="list.toggleLeftSide()">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <rect x="1.5" y="2.5" width="13" height="11" rx="2" stroke="currentColor" stroke-width="1.4" />
          <line x1="6" y1="2.5" x2="6" y2="13.5" stroke="currentColor" stroke-width="1.4" />
        </svg>
      </button>
      <!-- 新建对话 -->
      <button class="header-btn" @click="list.newConversation()">
        <el-icon :size="18"><Plus /></el-icon>
      </button>
    </template>
    <div class="header-info">
      <img v-if="list.appInfo.value?.icon" :src="list.appInfo.value.icon" class="header-icon" />
      <div class="header-text">
        <span v-if="list.appInfo.value?.name" class="header-app-name">{{ list.appInfo.value.name }}</span>
        <span class="header-title">{{ list.currentConversation.value?.abstract || '新对话' }}</span>
      </div>
    </div>
    <slot />
  </header>
</template>

<script setup lang="ts">
import { Operation, Plus } from '@element-plus/icons-vue'
import { useConversationListStore } from '../../../left-sidebar/conversation-list/index'
import { useExecutionDetailStore } from '../../../right-sidebar/execution-detail/index'

const list = useConversationListStore()
const detail = useExecutionDetailStore()
</script>

<style scoped lang="scss">
.panel-header {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 44px;
  padding: 0 12px;
  flex-shrink: 0;
  border-bottom: 1px solid var(--bd, #dcdfe6);
}
.header-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  color: var(--t2, #606266);
  flex-shrink: 0;
}
.header-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}
.header-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}
.header-icon {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  object-fit: cover;
  flex-shrink: 0;
}
.header-text {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.header-app-name {
  font-size: 11px;
  font-weight: 400;
  color: var(--t3, #909399);
  line-height: 1.2;
}
.header-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--t1, #303133);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
