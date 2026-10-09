<template>
  <!-- portal 视图:在 chat 视图基础上把左侧换成按智能体分组的门户历史对话 -->
  <ConversationLayout
    :left-open="bundle.list.leftSideOpen.value"
    :right-open="bundle.detail.rightSideOpen.value"
    :left-mode="leftMode"
    :right-mode="rightMode"
    @mask-click="closeDrawers"
  >
    <template #left><PortalConversationList /></template>
    <template #main>
      <!-- 全部智能体页显示智能体卡片，其余显示对话面板 -->
      <PortalApplicationPanel v-if="bundle.portalList.isApplicationListActive.value" />
      <PortalChatPanel v-else />
    </template>
    <template #right><ExecutionDetail /></template>
  </ConversationLayout>
  <!-- 没有当前智能体时新建对话，选择智能体 -->
  <SelectApplicationDrawer ref="applicationSelectorRef" />
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onBeforeUnmount, provide } from 'vue'
import ConversationLayout from '../../core/layout/index.vue'
import PortalConversationList from '../../left-sidebar/portal-conversation-list/index.vue'
import SelectApplicationDrawer from '../../left-sidebar/portal-conversation-list/SelectApplicationDrawer.vue'
import PortalChatPanel from '../../main/portal-chat-panel/index.vue'
import PortalApplicationPanel from '../../main/portal-application-panel/index.vue'
import ExecutionDetail from '../../right-sidebar/execution-detail/index.vue'
import { CONVERSATION_LIST_KEY } from '../../left-sidebar/conversation-list/index'
import { MESSAGE_LIST_KEY } from '../../components/message-list/index'
import { MESSAGE_INPUT_KEY } from '../../components/message-input/index'
import { EXECUTION_DETAIL_KEY } from '../../right-sidebar/execution-detail/index'
import { PORTAL_CONVERSATION_LIST_KEY } from '../../left-sidebar/portal-conversation-list/index'
import { createPortalConversation } from './index'

const applicationSelectorRef = ref<InstanceType<typeof SelectApplicationDrawer>>()
const bundle = createPortalConversation({ openApplicationSelector: () => applicationSelectorRef.value?.open() })

// 各组件 store 由本视图 provide(视图是左/主/右的共同祖先)
provide(CONVERSATION_LIST_KEY, bundle.list)
provide(MESSAGE_LIST_KEY, bundle.msgs)
provide(MESSAGE_INPUT_KEY, bundle.input)
provide(EXECUTION_DETAIL_KEY, bundle.detail)
provide(PORTAL_CONVERSATION_LIST_KEY, bundle.portalList)

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
  bundle.portalList.loadApplicationGroups()
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  bundle.msgs.cancel()
})

watch(isMobile, (m) => (bundle.list.leftSideOpen.value = !m))
// 新建或重新选择会话时，即使会话 ID 不变也收起左侧抽屉。
watch([() => bundle.list.currentChatId.value, () => bundle.list.composerResetSignal.value], () => {
  if (leftMode.value === 'drawer') bundle.list.leftSideOpen.value = false
})
</script>

<style lang="scss">
@use '../../index.scss';
</style>
