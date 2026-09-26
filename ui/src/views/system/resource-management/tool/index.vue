<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import SystemToolWorkflowApi from '@/api/admin/system/resource-management/tool/tool-workflow'
import SystemRelatedResourcesApi from '@/api/admin/system/resource-management/related-resources'
import SystemResourceTriggerApi from '@/api/admin/system/resource-management/resource-trigger'
import SystemCommonApi from '@/api/admin/system/common'
import SystemWorkspaceApi from '@/api/admin/system/workspace'
import type { Dict, OptionItem, ToolItem } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import { TOOL_TYPE_OPTIONS } from '@/constants'
import { useStore } from '@/stores'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
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

const { auth } = useStore()
const router = useRouter()

/* 工具分页与筛选 */
const loading = ref(false)
const operationLoading = ref(false)
const tools = ref<ToolItem[]>([])
const pagination = ref({ currentPage: 1, pageSize: 20, total: 0 })
const toolQuery = ref<Dict<unknown>>()
const creatorOptions = ref<OptionItem<string>[]>([])
const workspaceOptions = ref<OptionItem<string>[]>([])
const selectedWorkspaceIds = ref<string[]>([])
const searchFields = computed(() => [
  { label: '名称', value: 'name' },
  { label: '类型', value: 'tool_type', options: TOOL_TYPE_OPTIONS.filter(({ value }) => value) },
  {
    label: '来源',
    value: 'source',
    options: [
      { label: '工具商店', value: 'TOOL_STORE' },
      { label: '自定义', value: 'CUSTOM' },
    ],
  },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const toolTypeLabels = new Map(TOOL_TYPE_OPTIONS.map(({ value, label }) => [value, label]))

function loadCreatorOptions(keyword: string) {
  return SystemCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ value: id, label: nick_name }))
  })
}

function loadTools() {
  loading.value = true
  return SystemToolApi.getToolPage(pagination.value, {
    ...toolQuery.value,
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
    `确认删除工具：${tool.name}？`,
    tool.resource_count ? `该工具已被 ${tool.resource_count} 个资源引用，删除后相关资源将无法正常运行，请谨慎操作。` : '',
  )
    .then(() => {
      operationLoading.value = true
      return SystemToolApi.deleteTool(tool.id).then(() => {
        MsgSuccess('删除成功')
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
  <MkViewLayout>
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
        resizable
      >
        <el-table-column prop="name" label="名称" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="flex-align-center gap-2">
              <ToolIcon :icon="row.icon" :type="row.tool_type" :size="20" class="shrink-0" />
              <span class="truncate" :title="row.name">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="tool_type" label="类型" width="120">
          <template #default="{ row }">{{ toolTypeLabels.get(row.tool_type) ?? row.tool_type }}</template>
        </el-table-column>
        <el-table-column label="来源" width="120">
          <template #default="{ row }">{{ row.template_id ? '工具商店' : '自定义' }}</template>
        </el-table-column>
        <el-table-column label="启用状态" width="100">
          <template #default="{ row }"><MkStatusLabel :active="row.is_active" /></template>
        </el-table-column>
        <el-table-column v-if="auth.isEE" prop="workspace_name" label="工作空间" min-width="160" show-overflow-tooltip>
          <template #header>
            <MkTableFilter v-model="selectedWorkspaceIds" label="工作空间" :options="workspaceOptions" @change="handleFilterChange" />
          </template>
        </el-table-column>
        <el-table-column prop="nick_name" label="创建者" min-width="120" show-overflow-tooltip />
        <el-table-column label="更新时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.update_time) }}</template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <div class="flex-align-center gap-1">
              <!-- 启用或禁用工具 -->
              <ToolStatusSwitch class="mr-1!" v-model:loading="operationLoading" :api="SystemToolApi" :tool="row" @update="handleToolUpdate" />
              <!-- 编辑工具配置 -->
              <EditToolAction display="button" label="编辑" :api="SystemToolApi" :tool="row" @update="handleToolUpdate" />
              <!-- 更多工具操作 -->
              <MkTableMoreDropdown persistent>
                <!-- 打开工具工作流 -->
                <MkDropdownItem v-if="row.tool_type === TOOL_TYPE.WORKFLOW" @click="handleOpenWorkflow(row, $event)">
                  <template #icon><MkIcon name="icon_setting" /></template>
                  工作流
                </MkDropdownItem>
                <!-- 配置启动参数 -->
                <InitParamAction
                  v-if="row.init_field_list?.length"
                  v-model:loading="operationLoading"
                  label="启动参数"
                  :api="SystemToolApi"
                  :tool="row"
                  @update="handleToolUpdate"
                />

                <!-- 资源授权 -->
                <AuthorizeToolAction label="资源授权" :tool="row" />
                <!-- 查看 MCP 配置 -->
                <McpConfigAction
                  v-if="row.tool_type === TOOL_TYPE.MCP"
                  v-model:loading="operationLoading"
                  label="MCP 配置详情"
                  :api="SystemToolApi"
                  :tool="row"
                />
                <!-- 查看触发器 -->
                <TriggerToolAction
                  :tool-api="SystemToolApi"
                  :tool-workflow-api="SystemToolWorkflowApi"
                  v-if="[TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW].includes(row.tool_type)"
                  label="触发器"
                  :api="SystemResourceTriggerApi"
                  :tool="row"
                />
                <!-- 查看关联资源 -->
                <RelatedResourcesToolAction label="查看关联资源" :api="SystemRelatedResourcesApi" :tool="row" />
                <!-- 查看执行记录 -->
                <ExecutionRecordToolAction
                  v-if="[TOOL_TYPE.CUSTOM, TOOL_TYPE.WORKFLOW].includes(row.tool_type)"
                  label="查看执行记录"
                  :api="SystemToolWorkflowApi"
                  :tool="row"
                />
                <!-- 导出工具 -->
                <ExportToolAction v-if="!row.template_id" v-model:loading="operationLoading" label="导出" :api="SystemToolApi" :tool="row" />
                <!-- 删除工具 -->
                <MkDropdownItem divided :disabled="operationLoading" @click="handleDeleteTool(row)">
                  <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                  删除
                </MkDropdownItem>
              </MkTableMoreDropdown>
            </div>
          </template>
        </el-table-column>
      </MkTable>
    </template>
  </MkViewLayout>
</template>
