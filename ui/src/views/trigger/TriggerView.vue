<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import CommonApi from '@/api/admin/workspace/common'
import { TRIGGER_TYPE } from '@/api/enums'
import type { Dict, OptionItem, Trigger, TriggerType } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import TriggerFormDrawer from './trigger-form/TriggerFormDrawer.vue'
import TriggerTaskPopover from './components/TriggerTaskPopover.vue'

/* 触发器筛选与分页查询 */
const loading = ref(false)
const triggerData = ref<Trigger[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const triggerQuery = ref<Dict<unknown>>({})
const triggerTypeLabels: Record<TriggerType, string> = {
  [TRIGGER_TYPE.SCHEDULED]: '定时触发',
  [TRIGGER_TYPE.EVENT]: '事件触发',
}
const creatorOptions = ref<OptionItem<string>[]>([])
const searchFields = computed(() => [
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
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])

function loadCreatorOptions(keyword: string) {
  return CommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function loadTriggers(): Promise<void> {
  loading.value = true
  return TriggerApi.getTriggerPage(paginationConfig.value, triggerQuery.value)
    .then((page) => {
      triggerData.value = page.records
      paginationConfig.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  tableRef.value?.clearSelection()
  triggerQuery.value = query ?? {}
  paginationConfig.value.currentPage = 1
  loadTriggers()
}

/* 新建、编辑 */
const triggerDrawerRef = ref<InstanceType<typeof TriggerFormDrawer>>()
const tableRef = ref<{ clearSelection: () => void }>()
const selectedTriggers = ref<Trigger[]>([])

function handleOpenTriggerDrawer(trigger?: Trigger) {
  triggerDrawerRef.value?.open(trigger?.id)
}

function handleDeleteTrigger(trigger: Trigger) {
  return MsgConfirm(`确定删除触发器“${trigger.name}”吗？`, '删除后将停止触发任务，并删除相关执行记录。')
    .then(() => {
      loading.value = true
      return TriggerApi.deleteTrigger(trigger.id)
        .then(() => {
          MsgSuccess('删除成功')
          tableRef.value?.clearSelection()
          return loadTriggers()
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

/* 启用状态在请求成功后更新，失败时保留原状态 */

function handleChangeStatus(trigger: Trigger) {
  const nextActive = !trigger.is_active

  return TriggerApi.putTrigger(trigger.id, { is_active: nextActive })
    .then(() => {
      MsgSuccess(nextActive ? '启用成功' : '禁用成功')
      return true
    })
    .catch(() => false)
}

/* 批量操作 */
function handleSelectionChange(selection: unknown[]) {
  selectedTriggers.value = selection as Trigger[]
}
function handleBatchActivate(isActive: boolean) {
  loading.value = true
  const triggerIds = selectedTriggers.value.map(({ id }) => id)
  return TriggerApi.putBatchActivateTrigger(triggerIds, isActive)
    .then(() => {
      MsgSuccess(isActive ? '批量启用成功' : '批量禁用成功')
      tableRef.value?.clearSelection()
      return loadTriggers()
    })
    .finally(() => {
      loading.value = false
    })
}

function handleBatchDelete() {
  const triggerIds = selectedTriggers.value.map(({ id }) => id)
  return MsgConfirm(`是否删除选中的 ${triggerIds.length} 个触发器？`)
    .then(() => {
      loading.value = true
      return TriggerApi.putBatchDeleteTrigger(triggerIds)
        .then(() => {
          MsgSuccess('批量删除成功')
          tableRef.value?.clearSelection()
          return loadTriggers()
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

onMounted(() => loadTriggers())
</script>

<template>
  <MkViewLayout :loading="loading">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex items-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 新建触发器 -->
          <el-button type="primary" @click="handleOpenTriggerDrawer()">
            <MkIcon name="icon_add_outlined" />
            <span>创建</span>
          </el-button>
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
        <el-table-column type="selection" width="48" reserve-selection />
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
        <el-table-column label="任务" min-width="180">
          <template #default="{ row }"><TriggerTaskPopover :tasks="row.trigger_task" /></template>
        </el-table-column>
        <el-table-column prop="create_user" label="创建者" width="130" show-overflow-tooltip />
        <el-table-column prop="create_time" label="创建时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="flex items-center gap-3">
              <!-- 修改触发器状态 -->
              <span @click.stop>
                <el-switch v-model="row.is_active" :before-change="() => handleChangeStatus(row)" size="small" class="mr-3" />
                <el-divider direction="vertical" />
              </span>

              <div class="flex">
                <!-- 编辑当前触发器 -->
                <el-tooltip content="编辑" placement="top">
                  <el-button type="primary" text @click.stop="handleOpenTriggerDrawer(row)">
                    <MkIcon name="icon_edit_outlined" />
                  </el-button>
                </el-tooltip>
                <!-- 删除当前触发器 -->

                <el-tooltip content="删除" placement="top">
                  <el-button type="primary" text @click.stop="handleDeleteTrigger(row)">
                    <MkIcon name="icon_delete-trash_outlined" />
                  </el-button>
                </el-tooltip>
              </div>
            </div>
          </template>
        </el-table-column>
        <template #footer-batch-actions>
          <!-- 批量启用所选触发器 -->
          <el-button type="primary" plain @click="handleBatchActivate(true)">启用</el-button>
          <!-- 批量禁用所选触发器 -->
          <el-button type="primary" plain @click="handleBatchActivate(false)">禁用</el-button>
          <!-- 批量删除所选触发器 -->
          <el-button type="danger" plain @click="handleBatchDelete">删除</el-button>
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <TriggerFormDrawer ref="triggerDrawerRef" @refresh="loadTriggers" />
</template>
