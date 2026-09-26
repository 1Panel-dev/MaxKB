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

<template>
  <!-- 面板挂载到 body，以视口定位，不参与工作流页面布局。 -->
  <Teleport to="body">
    <transition name="debug-panel">
      <div
        v-if="debug.visible.value"
        class="workflow-debug-panel overflow-hidden border border-N300 bg-white shadow-lg"
        :class="{ expanded: debug.expanded.value }"
      >
        <ConversationLayout
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
  </Teleport>
</template>

<style lang="scss">
@use '../../index.scss';

/* 调试面板定位与展开布局 */
.workflow-debug-panel {
  border-radius: 12px;
  bottom: calc(var(--spacing) * 3);
  height: min(calc(var(--spacing) * 170), 90vh);
  max-width: calc(100vw - var(--spacing) * 6);
  position: fixed;
  right: calc(var(--spacing) * 3);
  transition:
    width 0.25s ease-in-out,
    right 0.25s ease-in-out,
    bottom 0.25s ease-in-out,
    border-radius 0.25s ease-in-out;
  width: calc(var(--spacing) * 115);
  z-index: 20;

  &.expanded {
    border: none;
    border-radius: 0;
    bottom: 0;
    height: 100dvh;
    max-width: 100vw;
    right: 0;
    width: 50vw;

    /* 窗口变窄时增加面板占比，保留对话区可用宽度。 */
    @media (max-width: 1024px) {
      width: 90vw;
    }

    @media (max-width: 768px) {
      width: 100vw;
    }
  }
}

/* 使用透明度动画，避免面板横向位移超出视口。 */
.debug-panel-enter-active,
.debug-panel-leave-active {
  transition: opacity 0.25s ease;
}
.debug-panel-enter-from,
.debug-panel-leave-to {
  opacity: 0;
}
</style>
