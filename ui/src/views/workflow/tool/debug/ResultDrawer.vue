<script setup lang="ts">
import { computed, onBeforeUnmount, provide, ref } from 'vue'
import { cloneDeep } from 'lodash'
import WorkflowApi from '@/api/admin/workspace/tool/workflow'
import type { ToolWorkflowRecord } from '@/api/types'
import { MsgError } from '@/utils/message'
import { ConversationStream } from '@/conversation-panel/stream'
import { aggregators } from '@/conversation-panel'
import ContentList from '@/conversation-panel/content-list/index.vue'
import ExecutionDetailContent from '@/workflow-canvas/Execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'ToolWorkflowDebugResultDrawer' })
interface DebugBlock {
  id: string
  type: string
  content?: string
  [key: string]: unknown
}
interface DebugChunk {
  chat_record_id?: string
  content?: DebugBlock[]
}
interface ResumeParameters {
  formData?: Record<string, unknown>
  position?: unknown
  chunkId?: string
  chatRecordId?: string
}
const props = defineProps<{ toolId: string }>()
const running = defineModel<boolean>('running', { default: false })
const visible = ref(false)
const activeTab = ref('output')
const blocks = ref<DebugBlock[]>([])
const record = ref<ToolWorkflowRecord>()
const errorMessage = ref('')
let inputParameters: Record<string, unknown> = {}
let recordId = ''
let stream: ConversationStream | undefined
const executionDetails = computed(() => Object.values(record.value?.meta.details ?? {}))
const output = computed(() => JSON.stringify(record.value?.meta.output ?? {}, null, 2))

function receiveChunk(chunk: DebugChunk) {
  if (chunk.chat_record_id) recordId = chunk.chat_record_id
  for (const block of chunk.content ?? []) {
    const index = blocks.value.findIndex((entry) => entry.id === block.id)
    const previous = index < 0 ? {} : blocks.value[index]
    const merged = aggregators[block.type]?.(previous, block) ?? { ...previous, ...block }
    if (index < 0) blocks.value.push(merged)
    else blocks.value[index] = merged
  }
}

/* 流结束后查询记录；关闭只中断前端读取，不声明已取消服务端任务。 */
async function execute(extra: Record<string, unknown> = {}) {
  if (running.value) return
  running.value = true
  errorMessage.value = ''
  record.value = undefined
  try {
    const response = await WorkflowApi.postToolWorkflowDebug(props.toolId, { ...inputParameters, ...extra, chat_record_id: recordId })
    if (!visible.value) {
      await response.body?.cancel()
      return
    }
    if (!response.ok || !response.headers.get('content-type')?.includes('text/event-stream')) {
      const result = await response.json().catch(() => null)
      throw new Error(result?.message || `调试请求失败（${response.status}）`)
    }
    if (!response.body) throw new Error('未收到调试响应')
    let streamError: unknown
    stream = new ConversationStream(response, receiveChunk, (error?: unknown) => {
      if (error) streamError = error
      running.value = false
    })
    await stream.start()
    if (!visible.value) return
    if (streamError) throw streamError
    const result = await WorkflowApi.getToolWorkflowRecord(props.toolId, recordId)
    if (visible.value) record.value = result
  } catch (error) {
    if (visible.value) {
      errorMessage.value = error instanceof Error ? error.message : '调试失败'
      MsgError(errorMessage.value)
    }
  } finally {
    stream = undefined
  }
}

// 表单节点沿用同一条执行记录续跑，复用现有回复组件的 sendMessage 协议。
provide('sendMessage', (options: ResumeParameters) => {
  if (running.value || !visible.value) return
  return execute({ form_data: options.formData, chat_record_id: options.chatRecordId, chunk_id: options.chunkId, position: options.position })
})

function open(parameters: Record<string, unknown>) {
  if (running.value) return
  blocks.value = []
  record.value = undefined
  inputParameters = cloneDeep(parameters)
  recordId = crypto.randomUUID()
  activeTab.value = 'output'
  visible.value = true
  return execute()
}

function close() {
  visible.value = false
  stream?.cancel()
}

onBeforeUnmount(close)
defineExpose({ open, close })
</script>

<template>
  <MkDrawer v-model="visible" title="调试结果" :modal="false" @close="close">
    <template #header>
      <div class="-ml-2 flex items-center">
        <!-- 返回输入参数 -->
        <el-button class="mr-1" text @click="visible = false">
          <MkIcon name="icon_arrow-left_outlined" :size="20" />
        </el-button>
        <h4>调试结果</h4>
      </div>
    </template>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="输出" name="output">
        <h4 class="mk-title-decoration mb-4 mt-4">回复内容</h4>

        <!-- // TODO: 回复内容 调样式-->
        <el-card class="small" shadow="never">
          <ContentList :content-list="blocks" />
          <div v-if="running">回答中...</div>
        </el-card>

        <template v-if="record">
          <h4 class="mk-title-decoration my-4">输出参数</h4>
          <el-alert
            :title="record.state === 'SUCCESS' ? '运行成功' : '运行失败'"
            :type="record.state === 'SUCCESS' ? 'success' : 'error'"
            :closable="false"
            show-icon
            class="mb-4"
          />
          <p class="my-4">输出</p>
          <el-card class="small whitespace-pre-wrap" shadow="never" :class="{ 'border-danger': record.state !== 'SUCCESS' }">
            {{ output }}
          </el-card>
        </template>
      </el-tab-pane>
      <el-tab-pane label="执行详情" name="details">
        <!-- TODO 执行详情 -->
        <ExecutionDetailContent class="mt-6" :detail="executionDetails" :workflow-mode="WorkflowMode.Tool"></ExecutionDetailContent>
      </el-tab-pane>
    </el-tabs>
  </MkDrawer>
</template>
