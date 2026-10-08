<script setup lang="ts">
import { ref } from 'vue'
import type { KnowledgeSyncLog } from '@/api/types'
import { KNOWLEDGE_SYNC_OPTIONS } from '@/constants/knowledge'
import { datetimeFormat } from '@/utils/time'

// 暂无日志数据，保留表格结构和分页空态。
const syncLogs = ref<KnowledgeSyncLog[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 10, total: 0 })
</script>

<template>
  <MkTable v-model:pagination-config="paginationConfig" :data="syncLogs" :max-table-height="260">
    <el-table-column label="同步时间" width="180">
      <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
    </el-table-column>
    <el-table-column label="同步内容" min-width="320" show-overflow-tooltip>
      <template #default="{ row }"></template>
    </el-table-column>
    <el-table-column label="同步方式" width="140">
      <template #default="{ row }">{{ KNOWLEDGE_SYNC_OPTIONS.find((option) => option.value === row.sync_type)?.label ?? row.sync_type }}</template>
    </el-table-column>
    <el-table-column label="同步状态" width="120">
      <template #default="{ row }"></template>
    </el-table-column>
    <el-table-column label="耗时" width="110">
      <template #default="{ row }">{{ (row.duration_seconds ?? row.duration_ms / 1000).toFixed(2) }}s</template>
    </el-table-column>
  </MkTable>
</template>
