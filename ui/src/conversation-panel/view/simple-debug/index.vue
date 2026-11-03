<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, provide, ref, toRef, useTemplateRef, watch } from 'vue'
import type { AxiosProgressEvent } from 'axios'
import type { ApplicationDetail } from '@/api/types'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import ConversationLayout from '../../core/layout/index.vue'
import ChatPanel from '../../main/chat-panel/index.vue'
import ExecutionDetail from '../../right-sidebar/execution-detail/index.vue'
import SimpleDebugHeader from '../../components/header/simple-debug/index.vue'
import { CONVERSATION_LIST_KEY } from '../../left-sidebar/conversation-list/index'
import { MESSAGE_LIST_KEY } from '../../components/message-list/index'
import { MESSAGE_INPUT_KEY } from '../../components/message-input/index'
import { EXECUTION_DETAIL_KEY } from '../../right-sidebar/execution-detail/index'
import { createDebugConversation } from '../debug/index'

defineOptions({ name: 'SimpleDebugConversation' })

const props = defineProps<{
  /** 已保存的智能体详情；调试接口执行已保存、未发布的配置，页面保存后更新。 */
  application?: ApplicationDetail | null
}>()

defineSlots<{
  /** 左侧设置表单，收起时保留实例。 */
  setting?(): unknown
  /** 标题栏下方的页面提示，如设置未保存。 */
  notice?(): unknown
}>()

// 与工作流调试共用装配：Admin 调试接口、流式处理与各组件 store。
const bundle = createDebugConversation(toRef(props, 'application'))

// 动态表单上传使用当前会话，兼容文件字段的地址包装与取消操作。
provide('upload', (file: File, onProgress?: (percent: number, event: AxiosProgressEvent) => void) => {
  const upload = FileApi.postUploadFile(
    file,
    bundle.list.currentChatId.value,
    FILE_SOURCE_TYPE.CHAT,
    typeof onProgress === 'function' ? onProgress : undefined,
  )
  return Object.assign(
    upload.request.then((url) => ({ data: url })),
    { abort: upload.abort },
  )
})

provide(CONVERSATION_LIST_KEY, bundle.list)
provide(MESSAGE_LIST_KEY, bundle.msgs)
provide(MESSAGE_INPUT_KEY, bundle.input)
provide(EXECUTION_DETAIL_KEY, bundle.detail)

// 左栏放设置表单而非会话列表，开合复用会话列表 store 的 leftSideOpen；历史对话由标题栏浮层切换。
// 响应式按面板自身宽度判断（嵌在 Admin 页面内，窗口宽度不代表可用宽度）：窄时 drawer，宽时 push。
const SETTING_WIDTH = 520
const DETAIL_WIDTH = 420
// 两侧同时挤压展开时，对话区保留的最小宽度。
const MIN_CHAT_WIDTH = 400
const BREAKPOINT = 1000
const panelRef = useTemplateRef<HTMLElement>('panelRef')
const panelWidth = ref(BREAKPOINT)
const narrow = computed(() => panelWidth.value < BREAKPOINT)
const sideMode = computed(() => (narrow.value ? 'drawer' : 'push'))
const canPushBoth = computed(() => panelWidth.value >= SETTING_WIDTH + DETAIL_WIDTH + MIN_CHAT_WIDTH)

// 宽窄切换时同步开合：宽屏展开设置，窄屏收起设置和执行详情。
watch(
  narrow,
  (isNarrow) => {
    bundle.list.leftSideOpen.value = !isNarrow
    if (isNarrow) bundle.detail.closeRightSide()
  },
  { immediate: true },
)

// 挤压态放不下两侧时互相让位：后展开的一侧收起对侧；面板变窄时保留设置、收起执行详情。
watch(
  () => bundle.detail.rightSideOpen.value,
  (open) => {
    if (open && !narrow.value && !canPushBoth.value) bundle.list.leftSideOpen.value = false
  },
)
watch(
  () => bundle.list.leftSideOpen.value,
  (open) => {
    if (open && !narrow.value && !canPushBoth.value) bundle.detail.closeRightSide()
  },
)
watch(canPushBoth, (fits) => {
  if (!fits && !narrow.value && bundle.list.leftSideOpen.value) bundle.detail.closeRightSide()
})

const resizeObserver = new ResizeObserver(([entry]) => {
  if (entry) panelWidth.value = entry.contentRect.width
})
onMounted(() => {
  if (!panelRef.value) return
  // 首次绘制前同步测量，避免窄屏先以展开态渲染再收起。
  panelWidth.value = panelRef.value.clientWidth
  resizeObserver.observe(panelRef.value)
})
onBeforeUnmount(() => {
  resizeObserver.disconnect()
  bundle.msgs.cancel()
})

// 遮罩只在抽屉态出现，点击收起设置和执行详情。
const closeDrawers = () => {
  bundle.list.leftSideOpen.value = false
  bundle.detail.closeRightSide()
}

// 页面保存、发布校验失败时展开设置，显示错误字段。
defineExpose({ openSetting: () => (bundle.list.leftSideOpen.value = true) })
</script>

<template>
  <!-- 内嵌调试:左侧设置表单 + 主面板 + 右侧执行详情 -->
  <div ref="panelRef" class="mk-simple-debug h-full">
    <ConversationLayout
      :left-open="bundle.list.leftSideOpen.value"
      :right-open="bundle.detail.rightSideOpen.value"
      :left-mode="sideMode"
      :right-mode="sideMode"
      :left-width="SETTING_WIDTH"
      :right-width="DETAIL_WIDTH"
      @mask-click="closeDrawers"
    >
      <template #left><slot name="setting" /></template>
      <template #main>
        <ChatPanel>
          <template #header>
            <SimpleDebugHeader />
            <slot name="notice" />
          </template>
        </ChatPanel>
      </template>
      <template #right><ExecutionDetail /></template>
    </ConversationLayout>
  </div>
</template>

<style lang="scss">
@use '../../index.scss';

/* 设置表单使用白底；两侧抽屉沿用挤压宽度并限制占比，避免把对话区完全覆盖。 */
.mk-simple-debug .mk-conversation-side-panel {
  &.left {
    background: white;
  }

  &.drawer {
    max-width: 90%;

    .mk-conversation-side-panel__inner {
      width: 100%;
    }
  }

  &.right.drawer {
    --mk-conversation-side-panel-width: var(--mk-chat-right-width);
  }
}
</style>
