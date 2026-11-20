<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { Dict, OptionItem, ToolItem } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import SystemCommonApi from '@/api/admin/system/common'
import SystemRelatedResourcesApi from '@/api/admin/system/resource-management/related-resources'
import SystemResourceTriggerApi from '@/api/admin/system/resource-management/resource-trigger'
import SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import SystemToolWorkflowApi from '@/api/admin/system/resource-management/tool/tool-workflow'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import ToolStatusSwitch from '@/views/tool/tool-card/ToolStatusSwitch.vue'
import {
  AuthorizeToolAction,
  EditToolAction,
  ExecutionRecordToolAction,
  ExportToolAction,
  InitParamAction,
  McpConfigAction,
  RelatedResourcesToolAction,
  TriggerToolAction,
} from '@/views/tool/tool-card/action-dropdown'
import { TOOL_TYPE_OPTIONS } from '@/constants'
import { useStore } from '@/stores'
import { toOrderBy } from '@/utils/common'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { datetimeFormat } from '@/utils/time'
import perm from '@/permission'

const { t } = useI18n({ useScope: 'global' })

const { auth } = useStore()
const router = useRouter()

/* 工具分页与筛选 */
const loading = ref(false)
const operationLoading = ref(false)
const tools = ref<ToolItem[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const toolQuery = ref<Dict<unknown>>()
const orderBy = ref<string>()
const creatorOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedToolType = ref('')
const selectedSource = ref('')
const selectedStatus = ref('')
const selectedWorkspaceIds = ref<string[]>([])
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const toolTypeOptions = computed(() => TOOL_TYPE_OPTIONS.filter(({ value }) => value))
const sourceOptions = computed(() => [
  { label: t('tool.store.title'), value: 'TOOL_STORE' },
  { label: t('tool.source.custom'), value: 'CUSTOM' },
])
const statusOptions = computed(() => [
  { label: t('common.status.enabled'), value: 'enabled' },
  { label: t('common.status.disabled'), value: 'disabled' },
])
const toolTypeLabels = computed(() => new Map(TOOL_TYPE_OPTIONS.map(({ value, label }) => [value, label])))

function loadCreatorOptions(keyword: string) {
  return SystemCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ value: id, label: nick_name }))
  })
}

function loadTools() {
  loading.value = true
  return SystemToolApi.getToolPage(pagination.value, {
    ...toolQuery.value,
    order_by: orderBy.value,
    ...(selectedToolType.value ? { tool_type: selectedToolType.value } : {}),
    ...(selectedSource.value ? { source: selectedSource.value } : {}),
    ...(selectedStatus.value ? { status: selectedStatus.value } : {}),
    ...(selectedWorkspaceIds.value.length ? { workspace_ids: JSON.stringify(selectedWorkspaceIds.value) } : {}),
  })
    .then((page) => {
      tools.value = page.records
      pagination.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  toolQuery.value = query
  return handleFilterChange()
}

function handleFilterChange() {
  pagination.value.currentPage = 1
  return loadTools()
}

/* 表头排序：保留筛选并重新查询第一页。 */
function handleSortChange(sort: Parameters<typeof toOrderBy>[0]) {
  orderBy.value = toOrderBy(sort)
  return handleFilterChange()
}

/* 工具编辑、启停与工作流入口 */
function handleToolUpdate(tool: ToolItem) {
  const index = tools.value.findIndex(({ id }) => id === tool.id)
  if (index >= 0) tools.value.splice(index, 1, { ...tools.value[index], ...tool })
}

function handleOpenWorkflow(tool: ToolItem, event: MouseEvent) {
  const target = { name: 'system-resource-workflow-tool', params: { toolId: tool.id } }
  if (event.ctrlKey || event.metaKey) {
    window.open(router.resolve(target).href)
    return
  }
  return router.push(target)
}

/* 删除后重新查询，保留筛选并处理末页删空。 */
function handleDeleteTool(tool: ToolItem) {
  return MsgConfirm(
    t('tool.delete.title', { name: tool.name }),
    tool.resource_count ? t('tool.delete.description', { count: tool.resource_count }, tool.resource_count) : '',
  )
    .then(() => {
      operationLoading.value = true
      return SystemToolApi.deleteTool(tool.id).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
        if (tools.value.length === 1 && pagination.value.currentPage > 1) pagination.value.currentPage -= 1
        return loadTools()
      })
    })
    .catch(() => {})
    .finally(() => {
      operationLoading.value = false
    })
}

onMounted(() => {
  loadTools()
  if (auth.isEE) {
    SystemWorkspaceApi.getSystemWorkspaceList().then((workspaces) => {
      workspaceOptions.value = workspaces.flatMap(({ id, name }) => (id ? [{ value: id, label: name }] : []))
    })
  }
})
</script>

<template>
  <MkViewLayout :title="t('tool.title')">
    <template #default="{ Header, title }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
      </component>
      <MkTable
        v-model:pagination-config="pagination"
        v-loading="loading || operationLoading"
        :data="tools"
        :max-table-height="210"
        @current-change="loadTools"
        @size-change="loadTools"
        @sort-change="handleSortChange"
        resizable
      >
        <el-table-column prop="name" :label="t('common.name.label')" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <ToolIcon :icon="row.icon" :type="row.tool_type" :size="20" class="shrink-0" />
              <span class="truncate">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="tool_type" :label="t('common.labels.type')" width="120">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedToolType"
              :label="t('common.labels.type')"
              :options="toolTypeOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">{{ toolTypeLabels.get(row.tool_type) ?? row.tool_type }}</template>
        </el-table-column>
        <el-table-column :label="t('tool.source.label')" width="120">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedSource"
              :label="t('tool.source.label')"
              :options="sourceOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">{{ row.template_id ? t('tool.store.title') : t('tool.source.custom') }}</template>
        </el-table-column>
        <el-table-column :label="t('common.status.label')" width="100">
          <template #header>
            <MkTableFilter
              mode="single"
              v-model="selectedStatus"
              :label="t('common.status.label')"
              :options="statusOptions"
              @change="handleFilterChange"
            />
          </template>
          <template #default="{ row }">
            <MkStatusLabel :active="row.is_active" />
          </template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" prop="workspace_name" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter
              mode="multiple"
              v-model="selectedWorkspaceIds"
              :label="t('workspace.title')"
              filterable
              :options="workspaceOptions"
              @change="handleFilterChange"
            />
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" :label="t('common.labels.creator')" min-width="120" show-overflow-tooltip />
        <el-table-column prop="update_time" :label="t('common.labels.updateTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.update_time) }}</template>
        </el-table-column>
        <el-table-column prop="create_time" :label="t('common.labels.createTime')" width="180" sortable>
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column :label="t('common.labels.operation')" width="140" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center">
              <!-- 启用或禁用工具 -->
              <ToolStatusSwitch
                v-model:loading="operationLoading"
                :api="SystemToolApi"
                :tool="row"
                :disabled="!perm.tool.system.switch() || operationLoading"
                @update="handleToolUpdate"
              />
              <el-divider direction="vertical" class="ml-3! mr-2!" />
              <!-- 编辑工具配置 -->
              <EditToolAction
                v-if="perm.tool.system.edit()"
                display="button"
                :label="t('common.actions.edit')"
                :api="SystemToolApi"
                :tool="row"
                @update="handleToolUpdate"
              />
              <!-- 更多工具操作 -->
              <MkTableMoreDropdown>
                <!-- 打开工具工作流 -->
                <MkDropdownItem v-if="row.tool_type === TOOL_TYPE.WORKFLOW && perm.tool.system.edit()" @click="handleOpenWorkflow(row, $event)">
                  <template #icon><MkIcon name="icon_setting" /></template>
                  {{ t('tool.workflow.label') }}
                </MkDropdownItem>
                <!-- 启动参数 -->
                <InitParamAction
                  v-if="row.init_field_list?.length && perm.tool.system.edit()"
                  v-model:loading="operationLoading"
                  :label="t('tool.initParams.title')"
                  :api="SystemToolApi"
                  :tool="row"
                  @update="handleToolUpdate"
                />

                <!-- 资源授权 -->
                <AuthorizeToolAction v-if="perm.tool.system.auth()" :label="t('authorization.resource.title')" :tool="row" />
                <!-- 查看 MCP 配置 -->
                <McpConfigAction
                  v-if="row.tool_type === TOOL_TYPE.MCP"
                  v-model:loading="operationLoading"
                  :label="t('resource.mcpConfig.title')"
                  :api="SystemToolApi"
                  :tool="row"
                />
                <!-- 查看触发器 -->
                <TriggerToolAction
                  :tool-api="SystemToolApi"
                  :tool-workflow-api="SystemToolWorkflowApi"
                  v-if="[TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW].includes(row.tool_type) && perm.tool.system.triggerRead()"
                  :label="t('trigger.title')"
                  :api="SystemResourceTriggerApi"
                  :tool="row"
                />
                <!-- 查看关联资源 -->
                <RelatedResourcesToolAction
                  v-if="perm.tool.system.relateMap()"
                  :label="t('resource.relations.title')"
                  :api="SystemRelatedResourcesApi"
                  :tool="row"
                />
                <!-- 查看执行记录 -->
                <ExecutionRecordToolAction
                  v-if="[TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW].includes(row.tool_type) && perm.tool.system.record()"
                  :label="t('resource.executionRecords.view')"
                  :api="SystemToolWorkflowApi"
                  :tool="row"
                />
                <!-- 导出工具 -->
                <ExportToolAction
                  v-if="!row.template_id && perm.tool.system.export()"
                  v-model:loading="operationLoading"
                  :label="t('common.actions.export')"
                  :api="SystemToolApi"
                  :tool="row"
                />
                <!-- 删除工具 -->
                <MkDropdownItem @click="handleDeleteTool(row)" v-if="perm.tool.system.delete()">
                  <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                  {{ t('common.actions.delete') }}
                </MkDropdownItem>
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
