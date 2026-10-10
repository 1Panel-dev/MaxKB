<script setup lang="ts">
import { ref, watch } from 'vue'
import type SyncApi from '@/api/admin/workspace/knowledge/sync'
import { KNOWLEDGE_SYNC_STATUS, KNOWLEDGE_SYNC_TYPE } from '@/api/enums'
import type { KnowledgeSyncLog, KnowledgeSyncStatus } from '@/api/types'
import type { StatusLabelOptions } from '@/components/global/mk-status-label/types'
import { KNOWLEDGE_SYNC_OPTIONS } from '@/constants/knowledge'
import { datetimeFormat } from '@/utils/time'

defineOptions({ name: 'KnowledgeSyncLogTable' })
const props = defineProps<{ api: typeof SyncApi; knowledgeId: string }>()

// 进入日志页签、切换知识库和翻页时查询。
const loading = ref(false)
const syncLogs = ref<KnowledgeSyncLog[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 10, total: 0 })
const syncStatusOptions: Partial<Record<KnowledgeSyncStatus, StatusLabelOptions>> = {
  [KNOWLEDGE_SYNC_STATUS.RUNNING]: { type: 'loading', label: '同步中' },
  [KNOWLEDGE_SYNC_STATUS.SUCCESS]: { type: 'success', label: '成功' },
  [KNOWLEDGE_SYNC_STATUS.FAILURE]: { type: 'failure', label: '失败' },
}

function getSyncContent(log: KnowledgeSyncLog) {
  if (log.status === KNOWLEDGE_SYNC_STATUS.SKIPPED) {
    if (/already running|still running|already queued/.test(log.message)) return '有正在同步的任务，本次跳过'
    if (log.message === 'Scheduled synchronization is disabled') return '已关闭定时同步，本次跳过'
    return log.message || '本次同步已跳过'
  }
  const counts = [`已同步:${log.synced_count}`]
  if (log.skipped_count) counts.push(`跳过:${log.skipped_count}`)
  if (log.deleted_count) counts.push(`删除:${log.deleted_count}`)
  if (log.failed_count) counts.push(`失败:${log.failed_count}`)
  return `共${log.total_count}个文档 (${counts.join('，')})`
}
function loadSyncLogs() {
  if (loading.value) return
  loading.value = true
  return props.api
    .getKnowledgeSyncLogPage(props.knowledgeId, paginationConfig.value)
    .then((page) => {
      syncLogs.value = page.records
      paginationConfig.value.total = page.total
      paginationConfig.value.currentPage = page.current
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

watch(
  () => props.knowledgeId,
  () => {
    paginationConfig.value.currentPage = 1
    void loadSyncLogs()
  },
  { immediate: true },
)
</script>

<template>
  <div class="min-h-0 flex-1">
    <MkTable
      v-model:pagination-config="paginationConfig"
      v-loading="loading"
      :data="syncLogs"
      :max-table-height="260"
      @current-change="loadSyncLogs"
      @size-change="loadSyncLogs"
    >
      <el-table-column label="同步时间" width="200">
        <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
      </el-table-column>
      <el-table-column label="同步内容" min-width="400" show-overflow-tooltip>
        <template #default="{ row }">
          <span>{{ getSyncContent(row) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="同步方式" width="140">
        <template #default="{ row }">
          {{
            row.sync_type === KNOWLEDGE_SYNC_TYPE.COMPLETE
              ? '完整同步'
              : (KNOWLEDGE_SYNC_OPTIONS.find((option) => option.value === row.sync_type)?.label ?? row.sync_type)
          }}
        </template>
      </el-table-column>
      <el-table-column label="同步状态" width="120">
        <template #default="{ row }">
          <MkStatusLabel v-if="syncStatusOptions[row.status as KnowledgeSyncStatus]" v-bind="syncStatusOptions[row.status as KnowledgeSyncStatus]" />
        </template>
      </el-table-column>
      <el-table-column label="耗时" width="110">
        <template #default="{ row }">{{ (row.duration_seconds ?? row.duration_ms / 1000).toFixed(2) }}s</template>
      </el-table-column>
    </MkTable>
  </div>
</template>
