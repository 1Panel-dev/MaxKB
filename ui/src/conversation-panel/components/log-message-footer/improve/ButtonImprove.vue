<script setup lang="ts">
import type ChatLogApi from '@/api/admin/workspace/application/chat-log'
import { computed, ref } from 'vue'
import MarkDialog from './MarkDialog.vue'
import ImproveDialog from './ImproveDialog.vue'
import { useLogMessageListStore } from '../../log-message-list'

defineOptions({ name: 'ButtonImprove' })
const props = defineProps<{
  api: Pick<typeof ChatLogApi, 'putChatRecordLog' | 'getMarkChatRecord' | 'deleteMarkChatRecord'>
  applicationId: string
  chatId: string
  recordId: string
  answer: string
}>()
const { recordsById } = useLogMessageListStore()
const record = computed(() => recordsById.value[props.recordId]!)
const question = computed(() => record.value.question.content || '')
const activeDialog = ref<'improve' | 'mark' | null>(null)
const marked = computed(() => (record.value.improve_paragraph_id_list ?? []).length > 0)

function updateMarks(ids: string[]) {
  record.value.improve_paragraph_id_list = ids
}

function refreshMarks() {
  const { api, applicationId, chatId } = props
  return api
    .getMarkChatRecord(applicationId, chatId, props.recordId)
    .then((paragraphs) => updateMarks(paragraphs.map((paragraph) => String(paragraph.id))))
    .catch(() => {
      /* 请求层统一提示错误。 */
    })
}
</script>

<template>
  <!-- 打开修正内容弹窗 -->
  <MkTooltip :content="marked ? '查看标注' : '修正内容'">
    <el-button text @click="activeDialog = marked ? 'mark' : 'improve'">
      <MkIcon v-if="marked" name="icon_feedback_outlined" />
      <MkIcon v-else name="icon_edit_outlined" />
    </el-button>
  </MkTooltip>
  <ImproveDialog
    v-if="activeDialog === 'improve'"
    :api="api"
    :application-id="applicationId"
    :chat-id="chatId"
    :record-id="recordId"
    :question="question"
    :answer="answer"
    @saved="refreshMarks"
    @closed="activeDialog = null"
  />
  <MarkDialog
    v-else-if="activeDialog === 'mark'"
    :api="api"
    :application-id="applicationId"
    :chat-id="chatId"
    :record-id="recordId"
    @refresh="updateMarks"
    @closed="activeDialog = null"
  />
</template>
