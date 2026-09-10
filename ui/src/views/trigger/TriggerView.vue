<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import { TRIGGER_TYPE } from '@/api/enums'
import type { Dict, OptionItem, Trigger, TriggerType } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { perm } from '@/permission'
import TriggerFormDrawer from './TriggerFormDrawer.vue'

const triggerDrawerRef = ref<InstanceType<typeof TriggerFormDrawer>>()
const tableRef = ref<{ clearSelection: () => void }>()
const selectedTriggers = ref<Trigger[]>([])
const operating = ref(false)
const switchingIds = ref<string[]>([])
const canBatchOperate = computed(() => perm.trigger.edit() || perm.trigger.delete())

/* 新建、编辑及删除 */
function handleOpenTriggerDrawer(trigger?: Trigger) {
  triggerDrawerRef.value?.open(trigger?.id)
}

function handleDeleteTrigger(trigger: Trigger) {
  if (operating.value || !perm.trigger.delete()) return
  return MsgConfirm(`确定删除触发器“${trigger.name}”吗？`, '删除后将停止触发任务，并删除相关执行记录。')
    .then(() => {
      operating.value = true
      return TriggerApi.deleteTrigger(trigger.id)
        .then(() => {
          MsgSuccess('删除成功')
          tableRef.value?.clearSelection()
          return loadTriggers()
        })
        .finally(() => {
          operating.value = false
        })
    })
    .catch(() => {})
}

/* 启用状态在请求成功后更新，失败时保留原状态 */
function handleChangeState(trigger: Trigger) {
  if (switchingIds.value.includes(trigger.id) || !perm.trigger.edit()) return
  const isActive = !trigger.is_active
  switchingIds.value.push(trigger.id)
  return TriggerApi.putTrigger(trigger.id, { is_active: isActive })
    .then((detail) => {
      trigger.is_active = detail.is_active ?? isActive
      MsgSuccess(isActive ? '启用成功' : '禁用成功')
      return loadTriggers()
    })
    .finally(() => {
      switchingIds.value = switchingIds.value.filter((id) => id !== trigger.id)
    })
}

/* 跨页批量操作 */
function handleSelectionChange(selection: unknown[]) {
  selectedTriggers.value = selection as Trigger[]
}

function handleBatchActivate(isActive: boolean) {
  if (!selectedTriggers.value.length || operating.value || !perm.trigger.edit()) return
  operating.value = true
  const triggerIds = selectedTriggers.value.map(({ id }) => id)
  return TriggerApi.putBatchActivateTrigger(triggerIds, isActive)
    .then(() => {
      MsgSuccess(isActive ? '批量启用成功' : '批量禁用成功')
      tableRef.value?.clearSelection()
      return loadTriggers()
    })
    .finally(() => {
      operating.value = false
    })
}

function handleBatchDelete() {
  if (!selectedTriggers.value.length || operating.value || !perm.trigger.delete()) return
  const triggerIds = selectedTriggers.value.map(({ id }) => id)
  return MsgConfirm(`确定删除选中的 ${triggerIds.length} 个触发器吗？`, '删除后将停止触发任务，并删除相关执行记录。')
    .then(() => {
      operating.value = true
      return TriggerApi.putBatchDeleteTrigger(triggerIds)
        .then(() => {
          MsgSuccess('批量删除成功')
          tableRef.value?.clearSelection()
          return loadTriggers()
        })
        .finally(() => {
          operating.value = false
        })
    })
    .catch(() => {})
}

/* 触发器筛选与分页查询 */
const loading = ref(false)
const triggerData = ref<Trigger[]>([])
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

let queryVersion = 0
function loadTriggers(): Promise<void> {
  const version = ++queryVersion
  loading.value = true
  return TriggerApi.getTriggerPage(paginationConfig.value, triggerQuery.value)
    .then((page) => {
      if (version !== queryVersion) return
      const lastPage = Math.max(1, Math.ceil(page.total / paginationConfig.value.pageSize))
      if (paginationConfig.value.currentPage > lastPage) {
        paginationConfig.value.currentPage = lastPage
        return loadTriggers()
      }
      triggerData.value = page.records
      paginationConfig.value.total = page.total
    })
    .finally(() => {
      if (version === queryVersion) loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  tableRef.value?.clearSelection()
  triggerQuery.value = query ?? {}
  paginationConfig.value.currentPage = 1
  loadTriggers()
}

onMounted(loadTriggers)
</script>

<template>
  <MkViewLayout :loading="loading || operating">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex items-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 新建触发器 -->
          <el-button v-if="$perm.trigger.create()" type="primary" @click="handleOpenTriggerDrawer()">新建触发器</el-button>
        </div>
      </component>
      <MkTable
        ref="tableRef"
        row-key="id"
        @selection-change="handleSelectionChange"
        v-model:pagination-config="paginationConfig"
        :data="triggerData"
        :max-table-height="200"
        @current-change="loadTriggers"
        @size-change="loadTriggers"
        resizable
      >
        <el-table-column v-if="canBatchOperate" type="selection" width="48" reserve-selection />
        <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip>
          <template #default="{ row }"
            ><div class="flex items-center gap-2">
              <TriggerIcon :type="row.trigger_type" :size="24" /><span>{{ row.name }}</span>
            </div></template
          >
        </el-table-column>
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
        <el-table-column v-if="canBatchOperate" label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <el-switch
                v-if="$perm.trigger.edit()"
                :model-value="row.is_active"
                :loading="switchingIds.includes(row.id)"
                :disabled="operating"
                size="small"
                @change="handleChangeState(row)"
              />
              <!-- 编辑当前触发器 -->
              <el-button
                v-if="$perm.trigger.edit()"
                text
                type="primary"
                :disabled="switchingIds.includes(row.id) || operating"
                @click="handleOpenTriggerDrawer(row)"
                >编辑</el-button
              >
              <!-- 删除当前触发器 -->
              <el-button
                v-if="$perm.trigger.delete()"
                text
                type="danger"
                :disabled="switchingIds.includes(row.id) || operating"
                @click="handleDeleteTrigger(row)"
                >删除</el-button
              >
            </div>
          </template>
        </el-table-column>
        <template #footer-batch-actions>
          <!-- 批量启用所选触发器 -->
          <el-button
            v-if="$perm.trigger.edit()"
            :disabled="operating || !selectedTriggers.length || !!switchingIds.length"
            @click="handleBatchActivate(true)"
            >启用</el-button
          >
          <!-- 批量禁用所选触发器 -->
          <el-button
            v-if="$perm.trigger.edit()"
            :disabled="operating || !selectedTriggers.length || !!switchingIds.length"
            @click="handleBatchActivate(false)"
            >禁用</el-button
          >
          <!-- 批量删除所选触发器 -->
          <el-button
            v-if="$perm.trigger.delete()"
            type="danger"
            plain
            :disabled="operating || !selectedTriggers.length || !!switchingIds.length"
            @click="handleBatchDelete"
            >删除</el-button
          >
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <TriggerFormDrawer ref="triggerDrawerRef" @refresh="loadTriggers" />
</template>
