<template>
  <transition name="debug-panel">
    <div v-if="debug.visible.value" class="workflow-debug-panel" :class="{ expanded: debug.expanded.value }">
      <ConversationLayout
        class="h-full"
        :left-open="bundle.list.leftSideOpen.value"
        :right-open="bundle.detail.rightSideOpen.value"
        :left-mode="leftMode"
        :right-mode="rightMode"
        @mask-click="closeDrawers"
      >
        <template #left><ConversationList /></template>
        <template #main>
          <ChatPanel>
            <template #header><DebugHeader /></template>
          </ChatPanel>
        </template>
        <template #right><ExecutionDetail /></template>
      </ConversationLayout>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, provide, watch } from 'vue'
import ConversationLayout from '../../core/layout/index.vue'
import ConversationList from '../../left-sidebar/conversation-list/index.vue'
import ChatPanel from '../../main/chat-panel/index.vue'
import ExecutionDetail from '../../right-sidebar/execution-detail/index.vue'
import DebugHeader from '../../components/header/debug/index.vue'
import { CONVERSATION_LIST_KEY } from '../../left-sidebar/conversation-list/index'
import { MESSAGE_LIST_KEY } from '../../components/message-list/index'
import { MESSAGE_INPUT_KEY } from '../../components/message-input/index'
import { EXECUTION_DETAIL_KEY } from '../../right-sidebar/execution-detail/index'
import { createDebugHeaderStore, DEBUG_HEADER_KEY } from '../../components/header/debug/index'
import { createDebugConversation } from './index'

defineOptions({ name: 'DebugConversation' })

const bundle = createDebugConversation()

// 会话各组件 store + debug 面板状态,都由本视图 provide
provide(CONVERSATION_LIST_KEY, bundle.list)
provide(MESSAGE_LIST_KEY, bundle.msgs)
provide(MESSAGE_INPUT_KEY, bundle.input)
provide(EXECUTION_DETAIL_KEY, bundle.detail)

const debug = createDebugHeaderStore()
provide(DEBUG_HEADER_KEY, debug)
// open/close 暴露给工作流页通过 ref 调用
defineExpose({ open: debug.open, close: debug.close })

// 缩小(窄面板)用抽屉,放大(宽面板)用挤压——与窗口宽度无关,只看放大态
const leftMode = computed(() => (debug.expanded.value ? 'push' : 'drawer'))
const rightMode = computed(() => (debug.expanded.value ? 'push' : 'drawer'))

// 抽屉态:遮罩点击 / 切换会话 → 收起
const closeDrawers = () => {
  if (leftMode.value === 'drawer') bundle.list.leftSideOpen.value = false
  if (rightMode.value === 'drawer') bundle.detail.rightSideOpen.value = false
}
onMounted(() => {
  bundle.list.leftSideOpen.value = false // 菜单默认收起
  bundle.list.loadConversations()
})
onBeforeUnmount(() => bundle.msgs.cancel())
watch(
  () => bundle.list.currentChatId.value,
  () => {
    if (leftMode.value === 'drawer') bundle.list.leftSideOpen.value = false
  },
)
</script>

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

/* 放大:宽度占视口 50%,高度 100% */
.workflow-debug-panel.expanded {
  top: 0;
  right: 0;
  bottom: 0;
  width: 50vw;
  max-width: 100vw;
  border-radius: 0;
}

/* 面板内的对话框自带移动端样式:小屏下会把输入框 fixed 到整个视口。
   这里把它约束回面板内部,避免输入框脱离面板铺满视口。 */
.workflow-debug-panel :deep(.panel-input) {
  position: relative !important;
  left: auto !important;
  right: auto !important;
  bottom: auto !important;
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
