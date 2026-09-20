<template>
  <!-- chat 视图自组装:provide 各组件 store + 布局壳 + 左/主/右三区。窄屏抽屉、宽屏挤压 -->
  <ConversationLayout
    :left-open="bundle.list.leftSideOpen.value"
    :right-open="bundle.detail.rightSideOpen.value"
    :left-mode="leftMode"
    :right-mode="rightMode"
    @mask-click="closeDrawers"
  >
    <template #left><ConversationList /></template>
    <template #main><ChatPanel /></template>
    <template #right><ExecutionDetail /></template>
  </ConversationLayout>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, provide } from 'vue'
import ConversationLayout from '../../core/layout/index.vue'
import ConversationList from '../../left-sidebar/conversation-list/index.vue'
import ChatPanel from '../../main/chat-panel/index.vue'
import ExecutionDetail from '../../right-sidebar/execution-detail/index.vue'
import { CONVERSATION_LIST_KEY } from '../../left-sidebar/conversation-list/index'
import { MESSAGE_LIST_KEY } from '../../components/message-list/index'
import { MESSAGE_INPUT_KEY } from '../../components/message-input/index'
import { EXECUTION_DETAIL_KEY } from '../../right-sidebar/execution-detail/index'
import { createChatConversation } from './index'

const bundle = createChatConversation()

// 各组件 store 由本视图 provide(视图是左/主/右的共同祖先)
provide(CONVERSATION_LIST_KEY, bundle.list)
provide(MESSAGE_LIST_KEY, bundle.msgs)
provide(MESSAGE_INPUT_KEY, bundle.input)
provide(EXECUTION_DETAIL_KEY, bundle.detail)

// 响应式:窄屏 drawer,宽屏 push
const BREAKPOINT = 768
const isMobile = ref(window.innerWidth < BREAKPOINT)
const onResize = () => (isMobile.value = window.innerWidth < BREAKPOINT)
const leftMode = computed(() => (isMobile.value ? 'drawer' : 'push'))
const rightMode = computed(() => (isMobile.value ? 'drawer' : 'push'))

const closeDrawers = () => {
  if (leftMode.value === 'drawer') bundle.list.leftSideOpen.value = false
  if (rightMode.value === 'drawer') bundle.detail.rightSideOpen.value = false
}

onMounted(() => {
  window.addEventListener('resize', onResize)
  if (isMobile.value) bundle.list.leftSideOpen.value = false
  bundle.list.loadConversations()
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  bundle.msgs.cancel()
})

watch(isMobile, (m) => (bundle.list.leftSideOpen.value = !m))
watch(
  () => bundle.list.currentChatId.value,
  () => {
    if (isMobile.value) bundle.list.leftSideOpen.value = false
  },
)
</script>
