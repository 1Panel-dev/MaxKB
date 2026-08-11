<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { Filter } from '@element-plus/icons-vue'
import type { OptionItem, OperateLog, OperateLogQuery, WorkspaceItem } from '@/api/types'
import OperateLogApi from '@/api/admin/system/operate-log'
import WorkspaceApi from '@/api/admin/system/workspace'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess } from '@/utils/message'
import OperateLogDetailDialog from './dialog/OperateLogDetailDialog.vue'

type DatePreset = 7 | 30 | 90 | 183 | 'custom'
type SearchField = 'user' | 'ip_address' | 'status'

const detailDialogRef =
  useTemplateRef<InstanceType<typeof OperateLogDetailDialog>>('detailDialogRef')
const loading = ref(false)
const operateLogs = ref<OperateLog[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })

/* 日志筛选与列表 */
const datePreset = ref<DatePreset>(7)
const customDateRange = ref<[string, string]>()
const searchField = ref<SearchField>('user')
const searchValue = ref('')
const selectedMenus = ref<string[]>([])
const selectedWorkspaces = ref<string[]>([])
const menuOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const datePresetOptions: OptionItem<DatePreset>[] = [
  { label: '近 7 天', value: 7 },
  { label: '近 30 天', value: 30 },
  { label: '近 90 天', value: 90 },
  { label: '近半年', value: 183 },
  { label: '自定义', value: 'custom' },
]
const searchFieldOptions: OptionItem<SearchField>[] = [
  { label: '操作用户', value: 'user' },
  { label: 'IP 地址', value: 'ip_address' },
  { label: '状态', value: 'status' },
]
const statusOptions: OptionItem<string>[] = [
  { label: '成功', value: '200' },
  { label: '失败', value: '500' },
]

function formatDate(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const query = computed<OperateLogQuery>(() => {
  const params: OperateLogQuery = {}
  if (datePreset.value === 'custom') {
    params.start_time = customDateRange.value?.[0]
    params.end_time = customDateRange.value?.[1]
  } else {
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - datePreset.value)
    params.start_time = formatDate(startDate)
  }
  if (searchValue.value) params[searchField.value] = searchValue.value
  if (selectedMenus.value.length) params.menu = JSON.stringify(selectedMenus.value)
  if (selectedWorkspaces.value.length) {
    params.workspace_ids = JSON.stringify(selectedWorkspaces.value)
  }
  return params
})

function loadOperateLogs(resetPage = false) {
  if (resetPage) paginationConfig.value.currentPage = 1
  loading.value = true
  return OperateLogApi.getOperateLogPage(paginationConfig.value, query.value)
    .then((page) => {
      operateLogs.value = page.records
      paginationConfig.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchFieldChange() {
  searchValue.value = ''
  return loadOperateLogs(true)
}

function loadFilterOptions() {
  return Promise.all([
    OperateLogApi.getOperateLogMenuOptions().then((options) => {
      const uniqueOptions = new Map(options.map(({ menu, menu_label }) => [menu, menu_label]))
      menuOptions.value = [...uniqueOptions].map(([value, label]) => ({ label, value }))
    }),
    WorkspaceApi.getSystemWorkspaceList().then((workspaces: WorkspaceItem[]) => {
      workspaceOptions.value = workspaces.flatMap(({ id, name }) =>
        id ? [{ label: name, value: id }] : [],
      )
    }),
  ])
}

/* 日志导出 */
function handleExport() {
  loading.value = true
  return OperateLogApi.postOperateLogExport(query.value)
    .then((file) => {
      const url = URL.createObjectURL(file)
      const link = document.createElement('a')
      link.href = url
      link.download = 'operate-logs.xlsx'
      link.click()
      URL.revokeObjectURL(url)
    })
    .finally(() => {
      loading.value = false
    })
}

/* 日志清理策略 */
const cleanPolicyVisible = ref(false)
const cleanTime = ref(180)

function openCleanPolicy() {
  cleanPolicyVisible.value = true
}

function saveCleanPolicy() {
  loading.value = true
  return OperateLogApi.postOperateLogCleanTime(cleanTime.value)
    .then(() => {
      MsgSuccess('保存成功')
      cleanPolicyVisible.value = false
    })
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => {
  loadFilterOptions()
  OperateLogApi.getOperateLogCleanTime().then((days) => {
    cleanTime.value = days
  })
  loadOperateLogs()
})
</script>

<template>
  <section class="h-full px-6 py-4">
    <header class="mb-4 flex-between">
      <h4>操作日志</h4>
      <div class="flex gap-3">
        <el-button @click="handleExport">导出</el-button>
        <el-button @click="openCleanPolicy">清理策略</el-button>
      </div>
    </header>

    <div class="mb-4 flex-between gap-4">
      <div class="flex gap-3">
        <el-select v-model="datePreset" class="w-36" @change="loadOperateLogs(true)">
          <el-option
            v-for="option in datePresetOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-date-picker
          v-if="datePreset === 'custom'"
          v-model="customDateRange"
          type="daterange"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          value-format="YYYY-MM-DD"
          @change="loadOperateLogs(true)"
        />
      </div>
      <div class="flex gap-3">
        <el-select
          v-model="selectedMenus"
          multiple
          collapse-tags
          placeholder="操作类型"
          class="w-48"
          @change="loadOperateLogs(true)"
        >
          <template #prefix
            ><el-icon><Filter /></el-icon
          ></template>
          <el-option
            v-for="option in menuOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-select
          v-model="selectedWorkspaces"
          multiple
          collapse-tags
          placeholder="工作空间"
          class="w-48"
          @change="loadOperateLogs(true)"
        >
          <el-option
            v-for="option in workspaceOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-select v-model="searchField" class="w-28" @change="handleSearchFieldChange">
          <el-option
            v-for="option in searchFieldOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-select
          v-if="searchField === 'status'"
          v-model="searchValue"
          clearable
          placeholder="请选择状态"
          class="w-48"
          @change="loadOperateLogs(true)"
        >
          <el-option
            v-for="option in statusOptions"
            :key="option.value"
            :label="option.label"
            :value="option.value"
          />
        </el-select>
        <el-input
          v-else
          v-model="searchValue"
          clearable
          placeholder="请输入搜索内容"
          class="w-72"
          @change="loadOperateLogs(true)"
        />
      </div>
    </div>

    <MkTable
      v-model:pagination-config="paginationConfig"
      :data="operateLogs"
      v-loading="loading"
      @current-change="loadOperateLogs()"
      @size-change="loadOperateLogs()"
    >
      <el-table-column prop="menu" label="操作模块" min-width="140" />
      <el-table-column label="操作详情" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.operate
          }}{{ row.operation_object?.name ? `【${row.operation_object.name}】` : '' }}
        </template>
      </el-table-column>
      <el-table-column prop="user.username" label="操作用户" min-width="130" />
      <el-table-column prop="workspace_name" label="工作空间" min-width="160" />
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="row.status === 200 ? 'success' : 'danger'" effect="plain">
            {{ row.status === 200 ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="ip_address" label="IP 地址" width="150" />
      <el-table-column label="操作时间" width="180">
        <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="70" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="detailDialogRef?.open(row)">详情</el-button>
        </template>
      </el-table-column>
    </MkTable>

    <OperateLogDetailDialog ref="detailDialogRef" />
    <el-dialog v-model="cleanPolicyVisible" title="清理策略" width="440">
      <div class="flex items-center gap-2">
        <span>自动删除</span>
        <el-input-number v-model="cleanTime" :min="1" :max="100000" controls-position="right" />
        <span>天前的操作日志</span>
      </div>
      <template #footer>
        <el-button @click="cleanPolicyVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCleanPolicy">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>
