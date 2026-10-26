<script setup lang="ts">
import { provide, watch } from 'vue'
import ChatLogApi from '@/api/admin/workspace/application/chat-log'
import type { ChatLogRecord } from '@/api/types'
import ConversationLayout from '../../core/layout/index.vue'
import LogMessageList from '../../components/log-message-list/index.vue'
import ExecutionDetail from '../../right-sidebar/execution-detail/index.vue'
import { LOG_MESSAGE_LIST_KEY, createLogMessageListStore } from '../../components/log-message-list/index'
import { EXECUTION_DETAIL_KEY, createExecutionDetailStore } from '../../right-sidebar/execution-detail/index'

defineOptions({ name: 'LogConversation' })

/** 对话日志分页接口入参，与各资源范围 chat-log API 的 getChatRecordLog 保持结构一致。 */
type ChatRecordApi = {
  getChatRecordLog: (
    applicationId: string,
    chatId: string,
    page: { currentPage: number; pageSize: number },
    orderAsc?: boolean,
  ) => Promise<{ records: ChatLogRecord[] }>
}

const props = withDefaults(defineProps<{ chatId: string; applicationId?: string; chatLogApi?: ChatRecordApi; rightDrawerTarget?: HTMLElement }>(), {
  chatLogApi: () => ChatLogApi,
})

// 只读日志:只读消息列表 + 执行详情,无会话列表、无输入框。
// 不注入 MESSAGE_LIST_KEY,表单等内容项拿不到发送能力即自动只读。
const msgs = createLogMessageListStore({
  // 降序取(最新在前),store 页内 reverse 成正序、上滑加载更旧
  pageRecords: (cid, p, s) => props.chatLogApi.getChatRecordLog(props.applicationId || '', cid, { currentPage: p, pageSize: s }, false),
  getChatId: () => props.chatId,
})
const detail = createExecutionDetailStore()

provide(LOG_MESSAGE_LIST_KEY, msgs)
provide(EXECUTION_DETAIL_KEY, detail)

// 切换日志(抽屉内上一个/下一个)时收起执行详情并重新加载
watch(
  () => props.chatId,
  () => {
    detail.closeRightSide()
    msgs.load()
  },
  { immediate: true },
)
</script>

<template>
  <ConversationLayout
    :left-open="false"
    :right-open="detail.rightSideOpen.value"
    right-mode="drawer"
    :right-drawer-target="props.rightDrawerTarget"
    @mask-click="detail.closeRightSide()"
  >
    <template #main>
      <main class="mk-conversation-main">
        <LogMessageList :key="props.chatId" />
      </main>
    </template>
    <template #right><ExecutionDetail /></template>
  </ConversationLayout>
</template>

<style lang="scss">
@use '../../index.scss';
</style>
