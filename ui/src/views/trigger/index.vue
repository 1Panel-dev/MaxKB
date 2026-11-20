<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Dict, OptionItem, Trigger, TriggerType } from '@/api/types'
import { TRIGGER_TYPE } from '@/api/enums'
import CommonApi from '@/api/admin/workspace/common'
import TriggerApi from '@/api/admin/workspace/trigger/trigger'
import TriggerTaskPopover from './components/TriggerTaskPopover.vue'
import TriggerTaskRecordDrawer from './execution-record/TriggerTaskRecordDrawer.vue'
import TriggerFormDrawer from './trigger-form/TriggerFormDrawer.vue'
import { toOrderBy } from '@/utils/common'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })

/* 触发器筛选与分页查询 */
const loading = ref(false)
const triggerData = ref<Trigger[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const triggerSearchQuery = ref<Dict<unknown>>({})
const orderBy = ref<string>()
const triggerTypeLabels = computed<Record<TriggerType, string>>(() => ({
  [TRIGGER_TYPE.SCHEDULED]: t('trigger.scheduled.label'),
  [TRIGGER_TYPE.EVENT]: t('trigger.event.label'),
}))
const triggerTypeOptions = computed(() => Object.entries(triggerTypeLabels.value).map(([value, label]) => ({ value, label })))
const triggerStatusOptions = computed(() => [
  { label: t('common.status.enabled'), value: true },
  { label: t('common.status.disabled'), value: false },
])
const creatorOptions = ref<OptionItem<string>[]>([])
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  { label: t('trigger.labels.task'), value: 'task' },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const selectedTriggerType = ref<string | null>(null)
const selectedStatus = ref<boolean | null>(null)
const triggerQuery = computed<Dict<unknown>>(() => ({
  ...triggerSearchQuery.value,
  order_by: orderBy.value,
  ...(selectedTriggerType.value ? { type: selectedTriggerType.value } : {}),
  ...(selectedStatus.value !== null ? { is_active: selectedStatus.value } : {}),
}))

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
  triggerSearchQuery.value = query ?? {}
  paginationConfig.value.currentPage = 1
  loadTriggers()
}

function handleFilterChange() {
  tableRef.value?.clearSelection()
  paginationConfig.value.currentPage = 1
  loadTriggers()
}

/* 表头排序：清空选择并重新查询第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort)
  handleFilterChange()
}

/* 新建、编辑 */
const recordDrawerRef = ref<InstanceType<typeof TriggerTaskRecordDrawer>>()
const triggerDrawerRef = ref<InstanceType<typeof TriggerFormDrawer>>()
const tableRef = ref<{ clearSelection: () => void }>()
const selectedTriggers = ref<Trigger[]>([])

function handleOpenTriggerDrawer(trigger?: Trigger) {
  triggerDrawerRef.value?.open(trigger?.id)
}

function handleOpenRecordDrawer(trigger: Trigger) {
  recordDrawerRef.value?.open(trigger.id)
}

function handleDeleteTrigger(trigger: Trigger) {
  return MsgConfirm(t('trigger.delete.title', { name: trigger.name }), t('trigger.delete.description'))
    .then(() => {
      loading.value = true
      return TriggerApi.deleteTrigger(trigger.id)
        .then(() => {
          MsgSuccess(t('common.messages.deleteSuccess'))
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
      MsgSuccess(nextActive ? t('common.messages.enableSuccess') : t('common.messages.disableSuccess'))
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
      MsgSuccess(isActive ? t('common.messages.batchEnableSuccess') : t('common.messages.batchDisableSuccess'))
      tableRef.value?.clearSelection()
      return loadTriggers()
    })
    .finally(() => {
      loading.value = false
    })
}

function handleBatchDelete() {
  const triggerIds = selectedTriggers.value.map(({ id }) => id)
  return MsgConfirm(t('trigger.delete.batchTitle', { count: triggerIds.length }, triggerIds.length))
    .then(() => {
      loading.value = true
      return TriggerApi.putBatchDeleteTrigger(triggerIds)
        .then(() => {
          MsgSuccess(t('common.messages.batchDeleteSuccess'))
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
  <MkViewLayout :title="t('trigger.title')" :loading="loading">
    <template #default="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <!-- 新建触发器 -->
          <el-button v-if="perm.trigger.create()" type="primary" @click="handleOpenTriggerDrawer()">
            <MkIcon name="icon_add_outlined" />
            <span>{{ t('common.actions.create') }}</span>
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
        @sort-change="handleSortChange"
        resizable
      >
        <el-table-column type="selection" width="40" />
        <el-table-column prop="name" :label="t('common.name.label')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <TriggerIcon :type="row.trigger_type" :size="24" />
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_type" :label="t('common.labels.type')" width="120">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedTriggerType"
              :label="t('common.labels.type')"
              :options="triggerTypeOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">{{ triggerTypeLabels[row.trigger_type as TriggerType] || row.trigger_type }}</template>
        </el-table-column>
        <el-table-column prop="is_active" :label="t('common.status.activeLabel')" width="120">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedStatus"
              :label="t('common.status.activeLabel')"
              :options="triggerStatusOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }"><MkStatusLabel :active="row.is_active" /></template>
        </el-table-column>
        <el-table-column prop="desc" :label="t('common.description.label')" min-width="170" show-overflow-tooltip />
        <el-table-column prop="next_run_time" :label="t('trigger.labels.nextRunTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.next_run_time) || '-' }}</template>
        </el-table-column>
        <el-table-column :label="t('trigger.labels.task')" min-width="180">
          <template #default="{ row }"><TriggerTaskPopover :tasks="row.trigger_task" /></template>
        </el-table-column>
        <el-table-column prop="create_user" :label="t('common.labels.creator')" width="130" show-overflow-tooltip />
        <el-table-column prop="create_time" :label="t('common.labels.createTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.labels.operation')" width="160" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- 修改触发器状态 -->

              <el-switch v-model="row.is_active" :disabled="!perm.trigger.edit()" :before-change="() => handleChangeStatus(row)" size="small" />
              <el-divider direction="vertical" class="ml-3! mr-2!" />

              <div class="flex">
                <!-- 编辑当前触发器 -->
                <MkTooltip :content="t('common.actions.edit')" placement="top">
                  <el-button type="primary" text @click.stop="handleOpenTriggerDrawer(row)">
                    <MkIcon name="icon_edit_outlined" />
                  </el-button>
                </MkTooltip>

                <!-- 查看触发器执行记录 -->
                <MkTooltip :content="t('resource.executionRecords.title')" placement="top" v-if="perm.trigger.record()">
                  <el-button type="primary" text @click.stop="handleOpenRecordDrawer(row)">
                    <MkIcon name="icon_schedule-report_outlined" />
                  </el-button>
                </MkTooltip>

                <!-- 删除当前触发器 -->
                <MkTooltip :content="t('common.actions.delete')" placement="top" v-if="perm.trigger.delete()">
                  <el-button type="primary" text @click.stop="handleDeleteTrigger(row)">
                    <MkIcon name="icon_delete-trash_outlined" />
                  </el-button>
                </MkTooltip>
              </div>
            </div>
          </template>
        </el-table-column>
        <template #footer-batch-actions>
          <!-- 批量启用所选触发器 -->
          <el-button v-if="perm.trigger.edit()" type="primary" plain @click="handleBatchActivate(true)">{{ t('common.actions.enable') }}</el-button>
          <!-- 批量禁用所选触发器 -->
          <el-button v-if="perm.trigger.edit()" type="primary" plain @click="handleBatchActivate(false)">{{ t('common.actions.disable') }}</el-button>
          <!-- 批量删除所选触发器 -->
          <el-button v-if="perm.trigger.delete()" type="danger" plain @click="handleBatchDelete">{{ t('common.actions.delete') }}</el-button>
        </template>
      </MkTable>
    </template>
  </MkViewLayout>
  <TriggerTaskRecordDrawer ref="recordDrawerRef" />
  <TriggerFormDrawer :can-edit="perm.trigger.edit()" ref="triggerDrawerRef" @refresh="loadTriggers" :can-create="perm.trigger.create()"/>
</template>
