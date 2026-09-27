<script setup lang="ts">
import { computed, nextTick, onMounted, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import type { TableColumnCtx } from 'element-plus'
import ChatLogApi from '@/api/admin/workspace/application/chat-log'
import type { ChatLog, ChatLogSource, Dict, OptionItem } from '@/api/types'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { beforeDay, datetimeFormat } from '@/utils/time'
import { useApplicationDetailContext } from '../context'
import ButtonCleanStrategy from './clean-strategy/ButtonCleanStrategy.vue'
import { CHAT_LOG_SOURCE_LABELS } from './constants'
import ChatLogDetailDrawer from './ChatLogDetailDrawer.vue'

defineOptions({ name: 'ApplicationChatLogView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const route = useRoute()
const applicationId = computed(() => String(route.params.applicationId ?? ''))
const { application } = useApplicationDetailContext()

// 日志搜索与日期筛选
const loading = ref(false)
const chatLogs = ref<ChatLog[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchFields: OptionItem<string>[] = [
  { label: '摘要', value: 'abstract' },
  { label: '用户', value: 'username' },
]
const chatLogSearchQuery = ref<Dict<unknown>>()
const chatLogDateQuery = ref({ start_time: beforeDay(7), end_time: beforeDay(0) })

function handleSearchChange(query?: Dict<unknown>) {
  chatLogSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  return loadChatLogs()
}

function handleDateFilterChange({ startTime, endTime }: MkDateRangeValue) {
  chatLogDateQuery.value = { start_time: startTime, end_time: endTime }
  paginationConfig.value.currentPage = 1
  return loadChatLogs()
}

// 反馈筛选的草稿、重置和确认由 MkTableFilter 管理
const feedbackResetValue = { min_star: 0, min_trample: 0 }
const feedbackFilter = ref({ ...feedbackResetValue })

function handleFeedbackChange() {
  paginationConfig.value.currentPage = 1
  return loadChatLogs()
}

const chatLogQuery = computed<Dict<unknown>>(() => ({
  ...chatLogSearchQuery.value,
  ...chatLogDateQuery.value,
  ...feedbackFilter.value,
  comparer: 'and',
}))

function loadChatLogs(currentPage = paginationConfig.value.currentPage): Promise<ChatLog[]> {
  // 自定义日期清空后等待重新选择，避免提交后端不接受的空日期。
  if (!chatLogDateQuery.value.start_time) {
    chatLogs.value = []
    selectedChatLogs.value = []
    paginationConfig.value.total = 0
    return Promise.resolve([])
  }
  loading.value = true
  return ChatLogApi.getChatLog(applicationId.value, { ...paginationConfig.value, currentPage }, chatLogQuery.value)
    .then((page) => {
      chatLogs.value = page.records
      paginationConfig.value.currentPage = currentPage
      paginationConfig.value.total = page.total
      selectedChatLogs.value = []
      return page.records
    })
    .finally(() => {
      loading.value = false
    })
}

function formatSource(source?: string) {
  return source ? (CHAT_LOG_SOURCE_LABELS[source as ChatLogSource] ?? source) : '-'
}

// 对话详情的打开、关闭与跨页切换
const detailDrawerRef = useTemplateRef<InstanceType<typeof ChatLogDetailDrawer>>('detailDrawerRef')
const detailChatLog = ref<ChatLog>()
const detailChatLogIndex = computed(() => chatLogs.value.findIndex((chatLog) => chatLog.id === detailChatLog.value?.id))
const previousChatLogDisabled = computed(
  () => loading.value || detailChatLogIndex.value < 0 || (detailChatLogIndex.value === 0 && paginationConfig.value.currentPage === 1),
)
const nextChatLogDisabled = computed(
  () =>
    loading.value ||
    detailChatLogIndex.value < 0 ||
    (paginationConfig.value.currentPage - 1) * paginationConfig.value.pageSize + detailChatLogIndex.value + 1 >= paginationConfig.value.total,
)

async function handleRowClick(chatLog: ChatLog, column?: TableColumnCtx<ChatLog>) {
  if (loading.value || column?.type === 'selection') return
  detailChatLog.value = chatLog
  await nextTick()
  detailDrawerRef.value?.open()
}

function handleMoveChatLog(direction: -1 | 1) {
  if (direction === -1 ? previousChatLogDisabled.value : nextChatLogDisabled.value) return
  const chatLog = chatLogs.value[detailChatLogIndex.value + direction]
  if (chatLog) {
    detailChatLog.value = chatLog
    return
  }
  return loadChatLogs(paginationConfig.value.currentPage + direction)
    .then((pageRecords) => {
      if (!detailChatLog.value) return
      const targetChatLog = direction === 1 ? pageRecords[0] : pageRecords.at(-1)
      if (targetChatLog) detailChatLog.value = targetChatLog
      else detailDrawerRef.value?.close()
    })
    .catch(() => {})
}

function handleDetailClosed() {
  detailChatLog.value = undefined
}

// 导出当前筛选结果；勾选时仅导出选中的日志
const selectedChatLogs = ref<ChatLog[]>([])
const exporting = ref(false)

function handleSelectionChange(selection: unknown[]) {
  selectedChatLogs.value = selection as ChatLog[]
}

function handleExport() {
  if (loading.value || exporting.value || !chatLogDateQuery.value.start_time) return
  exporting.value = true
  return ChatLogApi.postExportChatLog(applicationId.value, application.value?.name ?? '对话日志', chatLogQuery.value, {
    select_ids: selectedChatLogs.value.map(({ id }) => id),
  }).finally(() => {
    exporting.value = false
  })
}

onMounted(() => loadChatLogs())
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between gap-4">
      <h4 class="shrink-0">{{ title }}</h4>
      <div class="flex-align-center">
        <MkDateRange class="mr-3" @change="handleDateFilterChange" />
        <MkComplexSearch :fields="searchFields" class="mr-3" @change="handleSearchChange" />
        <!-- 导出对话日志 -->
        <el-button plain :loading="exporting" @click="handleExport">
          <MkIcon name="icon_export_outlined" />
          <span>导出</span>
        </el-button>
        <!-- 设置日志清除策略 -->
        <ButtonCleanStrategy :application-id="applicationId" />
      </div>
    </div>
  </Teleport>

  <MkTable
    v-loading="loading"
    v-model:pagination-config="paginationConfig"
    :data="chatLogs"
    :max-table-height="200"
    @current-change="loadChatLogs()"
    @size-change="loadChatLogs()"
    @selection-change="handleSelectionChange"
    @row-click="handleRowClick"
    row-class-name="cursor-pointer"
    resizable
  >
    <el-table-column type="selection" width="40" />
    <el-table-column prop="abstract" label="摘要" min-width="220" show-overflow-tooltip />
    <el-table-column prop="chat_record_count" label="对话提问数" width="100" />
    <el-table-column width="140">
      <template #header>
        <MkTableFilter
          v-model="feedbackFilter"
          mode="custom"
          label="用户反馈"
          width="180"
          :reset-value="feedbackResetValue"
          @change="handleFeedbackChange"
        >
          <template #default="{ value }">
            <div class="space-y-3">
              <div class="flex-between gap-2">
                <span>赞同 ≥</span>
                <el-input-number
                  v-model="value.min_star"
                  class="w-25!"
                  size="small"
                  controls-position="right"
                  align="left"
                  :min="0"
                  :value-on-clear="0"
                  step-strictly
                />
              </div>
              <div class="flex-between gap-2">
                <span>反对 ≥</span>
                <el-input-number
                  v-model="value.min_trample"
                  class="w-25!"
                  size="small"
                  controls-position="right"
                  align="left"
                  :min="0"
                  :value-on-clear="0"
                  step-strictly
                />
              </div>
            </div>
          </template>
        </MkTableFilter>
      </template>
      <template #default="{ row }">
        <span v-if="!row.star_num && !row.trample_num">-</span>
        <span v-else class="flex-align-center gap-3">
          <span v-if="row.star_num" class="flex-align-center gap-1">
            <MkIcon name="icon_thumbsup_filled" class="text-[#FFC60A]!" />
            {{ row.star_num }}
          </span>
          <span v-if="row.trample_num" class="flex-align-center gap-1">
            <MkIcon name="icon_thumbdown_filled" class="text-danger!" />
            {{ row.trample_num }}
          </span>
        </span>
      </template>
    </el-table-column>
    <el-table-column prop="mark_sum" label="改进标注" width="100" />
    <el-table-column label="用户" min-width="130" show-overflow-tooltip>
      <template #default="{ row }">{{ row.asker?.username || '-' }}</template>
    </el-table-column>
    <el-table-column label="IP 地址" width="140" show-overflow-tooltip>
      <template #default="{ row }">{{ row.ip_address || '-' }}</template>
    </el-table-column>
    <el-table-column label="来源" min-width="140" show-overflow-tooltip>
      <template #default="{ row }">{{ formatSource(row.source?.type) }}</template>
    </el-table-column>
    <el-table-column label="最近对话时间" width="180">
      <template #default="{ row }">{{ datetimeFormat(row.update_time) }}</template>
    </el-table-column>
    <template #footer-batch-actions>
      <!-- TODO 添加到知识库 -->
      <el-button type="primary" plain>添加到知识库</el-button>
    </template>
  </MkTable>
  <ChatLogDetailDrawer
    v-if="detailChatLog"
    ref="detailDrawerRef"
    :chat-log="detailChatLog"
    :loading="loading"
    :previous-disabled="previousChatLogDisabled"
    :next-disabled="nextChatLogDisabled"
    @previous="handleMoveChatLog(-1)"
    @next="handleMoveChatLog(1)"
    @closed="handleDetailClosed"
  />
</template>
