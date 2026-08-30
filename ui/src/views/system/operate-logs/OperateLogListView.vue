<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import OperateLogApi from '@/api/admin/system/operate-log'
import WorkspaceApi from '@/api/admin/system/workspace'
import MkDateRange from '@/components/mk-date-range/index.vue'
import type { Dict, OperateLog, OptionItem } from '@/api/types'
import type { MkDateRangeValue } from '@/components/mk-date-range/types'
import CleanStrategyDialog from './dialog/CleanStrategyDialog.vue'
import OperateLogDetailDialog from './dialog/OperateLogDetailDialog.vue'
import { beforeDay, datetimeFormat } from '@/utils/time'
import { useStore } from '@/stores'

const { auth } = useStore()
/* 日志筛选与列表 */
const loading = ref(false)
const operateLogs = ref<OperateLog[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchFields: OptionItem<string>[] = [
  { label: '操作用户', value: 'user' },
  { label: 'IP 地址', value: 'ip_address' },
  {
    label: '状态',
    value: 'status',
    options: [
      { label: '成功', value: '200' },
      { label: '失败', value: '500' },
    ],
  },
]
const operateLogSearchQuery = ref<Dict<unknown>>()

function handleSearchChange(query?: Dict<unknown>) {
  operateLogSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  loadOperateLogs()
}

// 时间筛选
const operateLogDateQuery = ref<Dict<unknown>>({ start_time: beforeDay(7), end_time: '' })

function handleDateFilterChange({ startTime, endTime }: MkDateRangeValue) {
  operateLogDateQuery.value = { start_time: startTime, end_time: endTime }
  paginationConfig.value.currentPage = 1
  loadOperateLogs()
}

// 操作菜单筛选
const selectedOperateMenus = ref<string[]>([])
const operateMenuOptions = ref<OptionItem<string>[]>([])

function loadOperateMenuOptions() {
  return OperateLogApi.getOperateLogMenuOptions().then((options) => {
    const uniqueMenus = new Map<string, string>()
    options.forEach(({ menu, menu_label }) => {
      if (!uniqueMenus.has(menu)) uniqueMenus.set(menu, menu_label)
    })
    operateMenuOptions.value = [...uniqueMenus].map(([value, label]) => ({ label, value }))
  })
}

function handleOperateMenuChange() {
  paginationConfig.value.currentPage = 1
  loadOperateLogs()
}

// 工作空间筛选
const selectedWorkspaceIds = ref<string[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])

function loadWorkspaceOptions() {
  if (!auth.isEE) return Promise.resolve()

  return WorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
    workspaceOptions.value = workspaces.flatMap(({ id, name }) => (id ? [{ label: name, value: id }] : []))
  })
}

function handleWorkspaceChange() {
  paginationConfig.value.currentPage = 1
  loadOperateLogs()
}

const operateLogQuery = computed<Dict<unknown>>(() => ({
  ...operateLogDateQuery.value,
  ...operateLogSearchQuery.value,
  ...(selectedOperateMenus.value.length ? { menu: JSON.stringify(selectedOperateMenus.value) } : {}),
  ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
}))

function loadOperateLogs(resetQuery = false) {
  if (resetQuery) {
    operateLogSearchQuery.value = undefined
    paginationConfig.value.currentPage = 1
  }
  loading.value = true
  return OperateLogApi.getOperateLogPage(paginationConfig.value, operateLogQuery.value)
    .then((page) => {
      operateLogs.value = page.records
      paginationConfig.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

/* API详情 */
const detailDialogRef = useTemplateRef<InstanceType<typeof OperateLogDetailDialog>>('detailDialogRef')

function handleOpenDetail(log: OperateLog) {
  detailDialogRef.value?.open(log)
}
/* 清除策略 */
const cleanStrategyDialogRef = useTemplateRef<InstanceType<typeof CleanStrategyDialog>>('cleanStrategyDialogRef')

function handleOpenCleanStrategy() {
  cleanStrategyDialogRef.value?.open()
}

/* 导出 */
function handleExport() {
  loading.value = true
  return OperateLogApi.exportOperateLog(operateLogQuery.value).finally(() => {
    loading.value = false
  })
}

onMounted(() => {
  loadOperateLogs()
  loadOperateMenuOptions()
  loadWorkspaceOptions()
})
</script>

<template>
  <MkViewLayout :loading="loading">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex items-center">
          <MkDateRange class="mr-3" @change="handleDateFilterChange" />
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" class="mr-3" />
          <el-button plain @click="handleExport">
            <MkIcon name="icon_export_outlined" />
            <span>导出</span>
          </el-button>
          <el-button plain @click="handleOpenCleanStrategy">
            <MkIcon name="icon_clear_outlined" />
            <span>清除策略</span>
          </el-button>
        </div>
      </component>

      <MkTable
        v-model:pagination-config="paginationConfig"
        :data="operateLogs"
        @current-change="loadOperateLogs()"
        @size-change="loadOperateLogs()"
        :max-table-height="200"
        resizable
      >
        <el-table-column prop="menu" min-width="140" show-overflow-tooltip>
          <template #header>
            <MkTableFilter v-model="selectedOperateMenus" label="操作菜单" :options="operateMenuOptions" @change="handleOperateMenuChange" />
          </template>
        </el-table-column>
        <el-table-column label="操作详情" min-width="220" show-overflow-tooltip>
          <template #default="{ row }"> {{ row.operate }}{{ row.operation_object?.name ? `【${row.operation_object.name}】` : '' }} </template>
        </el-table-column>
        <el-table-column label="操作用户" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.user?.username || '-' }}</template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" min-width="160">
          <template #header>
            <MkTableFilter v-model="selectedWorkspaceIds" label="工作空间" :options="workspaceOptions" @change="handleWorkspaceChange" />
          </template>
          <template #default="{ row }">{{ row.workspace_name || '-' }}</template>
        </el-table-column>
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <span class="inline-flex items-center gap-2">
              <span :class="row.status === 200 ? 'mk-dot-success' : 'mk-dot-danger'" />
              <span>{{ row.status === 200 ? '成功' : '失败' }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="IP 地址" width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ip_address || '-' }}</template>
        </el-table-column>
        <el-table-column label="操作时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="70" fixed="right">
          <template #default="{ row }">
            <el-tooltip effect="dark" content="API详情" placement="top">
              <el-button type="primary" text @click.stop="handleOpenDetail(row)">
                <MkIcon name="icon_describe_outlined" />
              </el-button>
            </el-tooltip>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
  <CleanStrategyDialog ref="cleanStrategyDialogRef" />
  <OperateLogDetailDialog ref="detailDialogRef" />
</template>
