<script setup lang="ts">
import { computed, onMounted, reactive, ref, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, OperateLog, OptionItem } from '@/api/types'
import type { MkDateRangeValue } from '@/components/global/mk-date-range/types'
import OperateLogApi from '@/api/admin/system/operate-log'
import WorkspaceApi from '@/api/admin/system/workspace'
import ButtonCleanStrategy from './clean-strategy/ButtonCleanStrategy.vue'
import OperateLogDetailDialog from './dialog/OperateLogDetailDialog.vue'
import { useStore } from '@/stores'
import { toOrderBy } from '@/utils/common'
import { beforeDay, datetimeFormat } from '@/utils/time'
import perm from '@/permission/index.ts'

const { locale, t } = useI18n({ useScope: 'global' })

const { auth } = useStore()
/* 日志筛选与列表 */
const loading = ref(false)
const operateLogs = ref<OperateLog[]>([])
const orderBy = ref<string>()
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const searchFields: OptionItem<string>[] = reactive([
  { label: computed(() => t('operateLog.operationDetails')), value: 'operate' },
  { label: computed(() => t('operateLog.operator')), value: 'user' },
  { label: computed(() => t('operateLog.ipAddress')), value: 'ip_address' },
])
const operateLogSearchQuery = ref<Dict<unknown>>()

function handleSearchChange(query?: Dict<unknown>) {
  operateLogSearchQuery.value = query
  paginationConfig.value.currentPage = 1
  loadOperateLogs()
}

// 时间筛选
const operateLogDateQuery = ref<Dict<unknown>>({ start_time: beforeDay(7), end_time: beforeDay(0) })

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

// 状态筛选
const selectedStatus = ref<number>()
const statusOptions: OptionItem<number>[] = reactive([
  { label: computed(() => t('common.status.success')), value: 200 },
  { label: computed(() => t('common.status.failure')), value: 500 },
])

function handleStatusChange() {
  paginationConfig.value.currentPage = 1
  loadOperateLogs()
}

const operateLogQuery = computed<Dict<unknown>>(() => ({
  ...operateLogDateQuery.value,
  ...operateLogSearchQuery.value,
  order_by: orderBy.value,
  ...(selectedOperateMenus.value.length ? { menu: JSON.stringify(selectedOperateMenus.value) } : {}),
  ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
  ...(selectedStatus.value != null ? { status: selectedStatus.value } : {}),
}))

/* 表头排序：重新查询第一页，保留当前筛选。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort)
  paginationConfig.value.currentPage = 1
  return loadOperateLogs()
}

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
/* 导出 */
function handleExport() {
  loading.value = true
  return OperateLogApi.exportOperateLog(operateLogQuery.value).finally(() => {
    loading.value = false
  })
}

// 切换语言后重新获取服务端翻译的日志和菜单，保留当前查询条件。
watch(locale, () => {
  loadOperateLogs()
  loadOperateMenuOptions()
})

onMounted(() => {
  loadOperateLogs()
  loadOperateMenuOptions()
  loadWorkspaceOptions()
})
</script>

<template>
  <MkViewLayout :title="t('operateLog.title')" :loading="loading">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex-align-center">
          <MkDateRange class="mr-3" @change="handleDateFilterChange" />
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" class="mr-3" />
          <!-- 清除策略 导出-->
          <el-button v-if="perm.system.operationLog.export()" plain @click="handleExport">
            <MkIcon name="icon_export_outlined" />
            <span>{{ t('common.actions.export') }}</span>
          </el-button>
          <!-- 清除策略 -->
          <ButtonCleanStrategy v-if="perm.system.operationLog.clearPolicy()" />
        </div>
      </component>

      <MkTable
        v-model:pagination-config="paginationConfig"
        :data="operateLogs"
        @current-change="loadOperateLogs()"
        @size-change="loadOperateLogs()"
        @sort-change="handleSortChange"
        :max-table-height="200"
        resizable
      >
        <el-table-column prop="menu" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter
              mode="multiple"
              v-model="selectedOperateMenus"
              :label="t('operateLog.menu')"
              :options="operateMenuOptions"
              @change="handleOperateMenuChange"
            />
          </template>
        </el-table-column>
        <el-table-column :label="t('operateLog.operationDetails')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">{{ row.operate }}{{ row.operation_object?.name ? `【${row.operation_object.name}】` : '' }}</template>
        </el-table-column>
        <el-table-column :label="t('operateLog.operator')" min-width="130" show-overflow-tooltip>
          <template #default="{ row }">{{ row.user?.username || '-' }}</template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" min-width="160">
          <template #header>
            <MkTableFilter
              mode="multiple"
              v-model="selectedWorkspaceIds"
              :label="t('workspace.title')"
              filterable
              :options="workspaceOptions"
              @change="handleWorkspaceChange"
            />
          </template>
          <template #default="{ row }">{{ row.workspace_name || '-' }}</template>
        </el-table-column>
        <el-table-column min-width="110">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedStatus"
              :label="t('common.status.label')"
              :options="statusOptions"
              @change="handleStatusChange"
            />
          </template>
          <template #default="{ row }">
            <span class="inline-flex items-center gap-2">
              <span :class="row.status === 200 ? 'mk-dot-success' : 'mk-dot-danger'" />
              <span>{{ row.status === 200 ? t('common.status.success') : t('common.status.failure') }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column :label="t('operateLog.ipAddress')" width="140" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ip_address || '-' }}</template>
        </el-table-column>
        <el-table-column prop="create_time" :label="t('operateLog.operationTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.labels.operation')" width="80" fixed="right">
          <template #default="{ row }">
            <MkTooltip effect="dark" :content="t('operateLog.apiDetails')" placement="top">
              <el-button type="primary" text @click.stop="handleOpenDetail(row)">
                <MkIcon name="icon_describe_outlined" />
              </el-button>
            </MkTooltip>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
  <OperateLogDetailDialog ref="detailDialogRef" />
</template>
