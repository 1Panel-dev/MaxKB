<script setup lang="ts">
import { ref } from 'vue'
import { Aim, Close, FullScreen } from '@element-plus/icons-vue'
import Conversation from '@/conversation-panel/index.vue'

defineOptions({ name: 'DebugPanel' })

/* 调试面板显隐与放大 */
const debugVisible = ref(false)
const debugExpanded = ref(false)

function open() {
  debugVisible.value = true
}

function close() {
  debugVisible.value = false
  debugExpanded.value = false
}

defineExpose({ open, close })
</script>

<template>
  <!-- 调试对话：右侧悬浮面板 -->
  <transition name="debug-panel">
    <div v-if="debugVisible" class="workflow-debug-panel" :class="{ expanded: debugExpanded }">
      <div class="debug-panel-actions">
        <!-- 放大或还原调试面板 -->
        <button type="button" class="debug-panel-btn" @click="debugExpanded = !debugExpanded">
          <MkIcon :icon="debugExpanded ? Aim : FullScreen" :size="16" />
        </button>
        <!-- 关闭调试 -->
        <button type="button" class="debug-panel-btn" @click="close">
          <MkIcon :icon="Close" :size="16" />
        </button>
      </div>
      <Conversation :defaultOpen="false" type="DEBUG" class="h-full" />
    </div>
  </transition>
</template>

<style scoped lang="scss">
.workflow-debug-panel {
  position: absolute;
  top: calc(var(--mk-header-height) + 12px);
  right: 12px;
  bottom: 12px;
  width: 460px;
  max-width: calc(100vw - 24px);
  z-index: 20;
  background: var(--mk-N0, #fff);
  border: 1px solid var(--mk-N200, #dcdfe6);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  overflow: hidden;
  transition:
    width 0.25s ease,
    top 0.25s ease,
    right 0.25s ease,
    bottom 0.25s ease,
    border-radius 0.25s ease;
}

/* 放大：宽度占视口 50%，高度 100% */
.workflow-debug-panel.expanded {
  top: 0;
  right: 0;
  bottom: 0;
  width: 50vw;
  max-width: 100vw;
  border-radius: 0;
}

/* 面板内的对话框自带移动端样式：小屏下会把输入框 fixed 到整个视口。
   这里把它约束回面板内部，避免输入框脱离面板铺满视口。 */
.workflow-debug-panel :deep(.panel-input) {
  position: relative !important;
  left: auto !important;
  right: auto !important;
  bottom: auto !important;
}

.debug-panel-actions {
  position: absolute;
  top: 12px;
  right: 12px;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 4px;
}

.debug-panel-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--mk-N600, #606266);
  cursor: pointer;
}
.debug-panel-btn:hover {
  background: rgba(0, 0, 0, 0.05);
}

.debug-panel-enter-active,
.debug-panel-leave-active {
  transition:
    transform 0.25s ease,
    opacity 0.25s ease;
}
.debug-panel-enter-from,
.debug-panel-leave-to {
  transform: translateX(16px);
  opacity: 0;
}
</style>
