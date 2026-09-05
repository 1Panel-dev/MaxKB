<script setup lang="ts">
import { ref, onMounted } from 'vue'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import { TRIGGER_TYPE } from '@/api/enums'
import type { Dict, OptionItem, Trigger, TriggerType } from '@/api/types'
import { datetimeFormat } from '@/utils/time'

/* 触发器筛选与分页查询 */
const loading = ref(false)
const triggers = ref<Trigger[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const triggerQuery = ref<Dict<unknown>>({})
const triggerTypeLabels: Record<TriggerType, string> = {
  [TRIGGER_TYPE.SCHEDULED]: '定时触发',
  [TRIGGER_TYPE.EVENT]: '事件触发',
}
const searchFields: OptionItem<string>[] = [
  { label: '名称', value: 'name' },
  {
    label: '类型',
    value: 'type',
    options: Object.entries(triggerTypeLabels).map(([value, label]) => ({ value, label })),
  },
  { label: '任务', value: 'task' },
  {
    label: '状态',
    value: 'is_active',
    options: [
      { label: '已启用', value: 'true' },
      { label: '已禁用', value: 'false' },
    ],
  },
]

function loadTriggers() {
  loading.value = true
  return TriggerApi.getTriggerPage(paginationConfig.value, triggerQuery.value)
    .then((page) => {
      triggers.value = page.records
      paginationConfig.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  triggerQuery.value = query ?? {}
  paginationConfig.value.currentPage = 1
  loadTriggers()
}

onMounted(loadTriggers)
</script>

<template>
  <MkViewLayout :loading="loading">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
      </component>
      <MkTable
        v-model:pagination-config="paginationConfig"
        :data="triggers"
        row-key="id"
        :max-table-height="200"
        @current-change="loadTriggers"
        @size-change="loadTriggers"
      >
        <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip />
        <el-table-column prop="trigger_type" label="类型" width="120">
          <template #default="{ row }">{{ triggerTypeLabels[row.trigger_type as TriggerType] || row.trigger_type }}</template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="120">
          <template #default="{ row }"><MkStatusLabel :active="row.is_active" /></template>
        </el-table-column>
        <el-table-column prop="desc" label="描述" min-width="170" show-overflow-tooltip />
        <el-table-column prop="next_run_time" label="下次执行时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.next_run_time) || '-' }}</template>
        </el-table-column>
        <el-table-column label="任务" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{
            row.trigger_task
              .map((task: Trigger['trigger_task'][number]) => task.name)
              .filter(Boolean)
              .join('、') || '-'
          }}</template>
        </el-table-column>
        <el-table-column prop="create_user" label="创建者" width="130" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
