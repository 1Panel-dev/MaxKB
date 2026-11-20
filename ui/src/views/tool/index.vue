<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { Dict, FolderItem, OptionItem, ToolItem, ToolStoreResponse, ToolType } from '@/api/types'
import { RESOURCE_TYPE, TOOL_TYPE } from '@/api/enums'
import StoreApi from '@/api/admin/store.ts'
import CommonSystemApi from '@/api/admin/system/common'
import CommonApi from '@/api/admin/workspace/common'
import RelatedResourcesApi from '@/api/admin/workspace/related-resources'
import SharedToolApi from '@/api/admin/workspace/shared/tool'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkflowApi from '@/api/admin/workspace/tool/workflow'
import ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import FolderTree from '@/components/business/folder-tree/index.vue'
import EditToolForm from '@/views/tool/tool-form/EditToolForm.vue'
import ButtonCreateTool from './components/ButtonCreateTool.vue'
import ButtonToolStore from './components/ButtonToolStore.vue'
import ToolCard from './tool-card/ToolCard.vue'
import ToolStatusSwitch from './tool-card/ToolStatusSwitch.vue'
import {
  AuthorizeToolAction,
  CopyToolAction,
  DeleteToolAction,
  ExecutionRecordToolAction,
  ExportToolAction,
  InitParamAction,
  McpConfigAction,
  MoveToolAction,
  RelatedResourcesToolAction,
  ToolWorkflowAction,
  TriggerToolAction,
} from './tool-card/action-dropdown'
import { FOLDER_ENTRY_ID } from '@/constants/folder'
import { TOOL_TYPE_OPTIONS } from '@/constants/tool'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import perm from '@/permission/index.ts'

const { t } = useI18n({ useScope: 'global' })

/* 当前文件夹 */

const selectedFolder = ref<FolderItem>()
const currentFolder = computed<FolderItem>(() => selectedFolder.value ?? { id: FOLDER_ENTRY_ID.ALL, name: t('tool.categories.all') })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder: FolderItem) {
  const folderChanged = folder.id !== currentFolder.value.id
  selectedFolder.value = folder
  if (folderChanged) {
    cancelBatchSelection()
    refreshTool()
  }
}
// 新建文件夹
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
function handleCreateFolder() {
  folderTreeRef.value?.openCreate()
}

/* 工具查询搜索列表 */
const toolsData = ref<ToolItem[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const creatorOptions = ref<OptionItem<string>[]>([])
const searchFields = computed(() => [
  { label: t('common.name.label'), value: 'name' },
  {
    label: t('common.status.label'),
    value: 'is_active',
    options: [
      { value: true, label: t('common.status.enabled') },
      { value: false, label: t('common.status.disabled') },
    ],
  },
  { label: t('common.labels.creator'), value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])
const toolQuery = ref<Dict<unknown>>()
function loadCreatorOptions(keyword: string) {
  const requestApi = isShared.value ? CommonSystemApi : CommonApi
  return requestApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: Dict<unknown>) {
  toolQuery.value = query
  refreshTool()
}

const toolType = ref<ToolType | ''>('')

function loadToolsPage(pagination: { currentPage: number; pageSize: number }) {
  const requestApi = isShared.value ? SharedToolApi : ToolApi
  const folderId = isShared.value ? {} : { folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL }
  return requestApi.getToolPage(pagination, { ...toolQuery.value, tool_type: toolType.value, ...folderId })
}

// 加载工具商店
const storeTools = ref<ToolStoreResponse['apps']>([])

function loadStoreTools() {
  StoreApi.getStoreToolList({ name: '' }).then((res) => {
    storeTools.value = res.apps
  })
}

/* 卡片打开工具 */
const route = useRoute()
const router = useRouter()
const editToolFormRef = useTemplateRef<InstanceType<typeof EditToolForm>>('editToolFormRef')

function handleOpenEditTool(tool: ToolItem) {
  if (!perm.tool.workspace.edit(tool.id)) return
  return editToolFormRef.value?.open(tool)
}

function handleOpenTool(tool: ToolItem, event: MouseEvent) {
  if (isShared.value || batchSelectionMode.value) return
  if (tool.tool_type !== TOOL_TYPE.WORKFLOW) return handleOpenEditTool(tool)

  const workflowRoute = {
    name: 'workflow-tool',
    params: { toolId: tool.id, workspaceId: route.params.workspaceId },
  } as const
  if (event.ctrlKey || event.metaKey) {
    window.open(router.resolve(workflowRoute).href)
    return
  }
  return router.push(workflowRoute)
}

/* 工具维护 */
const toolOperationLoading = ref(false)

function refreshTool() {
  selectedToolIds.value = []
  return infiniteScrollRef.value?.reset()
}

function handleToolUpdate(tool: ToolItem) {
  const toolIndex = toolsData.value.findIndex((item) => item.id === tool.id)
  if (toolIndex >= 0) toolsData.value.splice(toolIndex, 1, tool)
}

function handleDeleteTool(toolId: string) {
  const toolIndex = toolsData.value.findIndex((item) => item.id === toolId)
  if (toolIndex >= 0) toolsData.value.splice(toolIndex, 1)
}

/* 批量选择与操作 */
const batchSelectionMode = ref(false)
const selectedToolIds = ref<string[]>([])
const selectedToolCount = computed(() => selectedToolIds.value.length)
const toolIds = computed(() => toolsData.value.map(({ id }) => id))
const batchMoveToDialogRef = useTemplateRef<{ close: () => void; open: (currentFolderId?: string) => void }>('batchMoveToDialogRef')

function toggleBatchSelection() {
  batchSelectionMode.value = !batchSelectionMode.value
  selectedToolIds.value = []
}

function cancelBatchSelection() {
  batchSelectionMode.value = false
  selectedToolIds.value = []
}

function handleToolSelect(toolId: string, selected: boolean) {
  if (selected) {
    if (!selectedToolIds.value.includes(toolId)) selectedToolIds.value.push(toolId)
    return
  }

  selectedToolIds.value = selectedToolIds.value.filter((id) => id !== toolId)
}

function handleOpenBatchMove() {
  if (!selectedToolCount.value) return
  batchMoveToDialogRef.value?.open(currentFolder.value.id)
}

// 批量移动
function handleBatchMove(targetFolderId: string) {
  if (toolOperationLoading.value || !selectedToolCount.value) return
  const toolIds = [...selectedToolIds.value]

  toolOperationLoading.value = true
  return ToolApi.putBatchMoveTools(toolIds, targetFolderId)
    .then(() => {
      MsgSuccess(t('common.messages.moveSuccess'))
      batchMoveToDialogRef.value?.close()
      cancelBatchSelection()
      return refreshTool()
    })
    .finally(() => {
      toolOperationLoading.value = false
    })
}

// 批量删除
function handleBatchDelete() {
  if (!selectedToolCount.value) return
  const toolIds = [...selectedToolIds.value]

  MsgConfirm(`${t('tool.delete.batchTitle', { count: toolIds.length })}?`, t('common.dialogs.deleteWarning'), {
    cancelButtonText: t('common.actions.cancel'),
    confirmButtonText: t('common.actions.delete'),
  })
    .then(() => {
      toolOperationLoading.value = true
      return ToolApi.putBatchDeleteTools(toolIds).then(() => {
        MsgSuccess(t('common.messages.deleteSuccess'))
        cancelBatchSelection()
        return refreshTool()
      })
    })
    .catch(() => {})
    .finally(() => {
      toolOperationLoading.value = false
    })
}

onMounted(() => {
  loadStoreTools()
})
</script>

<template>
  <MkViewLayout :title="t('tool.title')" class="workspace-tool-view" collapsible resizable>
    <template v-if="perm.tool.workspace.folderReadWorkspace()" #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <MkTooltip v-if="perm.tool.workspace.folderCreateWorkspace()" :content="t('folder.actions.create')" placement="top">
          <el-button @click="handleCreateFolder" text type="primary" class="-mr-1">
            <MkIcon name="icon_add-folder_outlined" :size="18" />
          </el-button>
        </MkTooltip>
      </component>

      <FolderTree ref="folderTreeRef" :source="RESOURCE_TYPE.TOOL" @select="handleFolderSelect" draggable></FolderTree>
    </template>

    <template #default="{ Footer, Header }">
      <component :is="Header">
        <div class="flex-align-center min-w-0 flex-1 gap-4">
          <h4 class="min-w-0 truncate" :title="currentFolder.name">{{ currentFolder.name }}</h4>
          <el-divider direction="vertical" />
          <el-select v-model="toolType" class="w-30!" :empty-values="[null, undefined]" :value-on-clear="null" @change="refreshTool">
            <el-option v-for="option in TOOL_TYPE_OPTIONS" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
        </div>
        <div class="flex-align-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <template v-if="!isShared">
            <!-- 批量选择 -->
            <span>
              <el-button
                v-if="perm.tool.workspace.batchMove() || perm.tool.workspace.batchDelete()"
                :disabled="!toolsData.length"
                :type="batchSelectionMode ? 'primary' : undefined"
                plain
                @click="toggleBatchSelection"
              >
                <MkIcon name="icon_Batch_outlined" />
                <span>{{ batchSelectionMode ? t('common.actions.cancelSelection') : t('common.actions.batchSelect') }}</span>
              </el-button>
            </span>

            <template v-if="!batchSelectionMode">
              <!-- 工具商店 -->
              <ButtonToolStore :folder-id="currentFolder.id" @refresh="refreshTool" />
              <!-- 创建 -->
              <ButtonCreateTool v-if="perm.tool.workspace.create()" :folder-id="currentFolder.id" :api="ToolApi" @refresh="refreshTool" />
            </template>
          </template>
        </div>
      </component>
      <div v-loading="toolOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="toolsData" :load="loadToolsPage">
          <div class="mk-resource-card-grid">
            <template v-for="tool in toolsData" :key="tool.id">
              <ToolCard
                v-model:loading="toolOperationLoading"
                :disabled="isShared"
                :selectable="batchSelectionMode"
                :selected="selectedToolIds.includes(tool.id)"
                :shared="isShared"
                :store-tools="storeTools"
                :tool="tool"
                @click="handleOpenTool(tool, $event)"
                @selected="handleToolSelect(tool.id, $event)"
                @update="handleToolUpdate"
              >
                <template #actions>
                  <!-- 修改工具状态 -->
                  <ToolStatusSwitch
                    :disabled="!perm.tool.workspace.switch(tool.id)"
                    v-model:loading="toolOperationLoading"
                    :api="ToolApi"
                    :tool="tool"
                    @update="handleToolUpdate"
                  />
                  <el-divider direction="vertical" class="ml-1!" />
                </template>
                <template #action-dropdown>
                  <!-- 编辑工具 -->
                  <MkAction
                    v-if="perm.tool.workspace.edit(tool.id)"
                    :label="t('common.actions.edit')"
                    icon="icon_edit_outlined"
                    @click="handleOpenEditTool(tool)"
                  />
                  <ToolWorkflowAction
                    v-if="tool.tool_type === TOOL_TYPE.WORKFLOW && perm.tool.workspace.edit(tool.id)"
                    :label="t('tool.workflow.label')"
                    :tool="tool"
                  />
                  <!-- 复制 -->
                  <CopyToolAction
                    v-if="perm.tool.workspace.copy(tool.id)"
                    v-model:loading="toolOperationLoading"
                    :label="t('common.actions.duplicate')"
                    :api="ToolApi"
                    :tool="tool"
                    @refresh="refreshTool"
                  />
                  <InitParamAction
                    v-if="(tool.init_field_list?.length ?? 0) > 0 && perm.tool.workspace.edit(tool.id)"
                    v-model:loading="toolOperationLoading"
                    :label="t('tool.initParams.title')"
                    :api="ToolApi"
                    :tool="tool"
                    @update="handleToolUpdate"
                  />
                  <McpConfigAction
                    v-if="tool.tool_type === TOOL_TYPE.MCP"
                    v-model:loading="toolOperationLoading"
                    :label="t('resource.mcpConfig.title')"
                    :api="ToolApi"
                    :tool="tool"
                  />
                  <!-- 资源授权 -->
                  <AuthorizeToolAction v-if="perm.tool.workspace.auth(tool.id)" :label="t('authorization.resource.title')" :tool="tool" />

                  <!-- 工具触发器 -->
                  <TriggerToolAction
                    v-if="(tool.tool_type === TOOL_TYPE.CUSTOM || tool.tool_type === TOOL_TYPE.WORKFLOW) && perm.tool.workspace.triggerRead(tool.id)"
                    :label="t('trigger.title')"
                    :api="ResourceTriggerApi"
                    :tool="tool"
                  />
                  <!-- 查看关联资源 -->
                  <RelatedResourcesToolAction
                    v-if="perm.tool.workspace.relateMap(tool.id)"
                    :label="t('resource.relations.title')"
                    :api="RelatedResourcesApi"
                    :tool="tool"
                  />

                  <!-- 查看执行记录 -->
                  <ExecutionRecordToolAction
                    v-if="(tool.tool_type === TOOL_TYPE.CUSTOM || tool.tool_type === TOOL_TYPE.WORKFLOW) && perm.tool.workspace.record(tool.id)"
                    :label="t('resource.executionRecords.view')"
                    :api="WorkflowApi"
                    :tool="tool"
                  />
                  <!-- 移动到 -->
                  <MoveToolAction
                    v-if="perm.tool.workspace.move(tool.id)"
                    v-model:loading="toolOperationLoading"
                    :label="t('folder.actions.moveTo')"
                    :api="ToolApi"
                    :current-folder-id="currentFolder.id"
                    :tool="tool"
                    @delete="handleDeleteTool"
                  />
                  <!-- 导出 -->
                  <ExportToolAction
                    v-if="!tool.template_id && perm.tool.workspace.export(tool.id)"
                    v-model:loading="toolOperationLoading"
                    :label="t('common.actions.export')"
                    :api="ToolApi"
                    :tool="tool"
                  />
                  <!-- 删除 -->
                  <DeleteToolAction
                    v-if="perm.tool.workspace.delete(tool.id)"
                    v-model:loading="toolOperationLoading"
                    :label="t('common.actions.delete')"
                    :api="ToolApi"
                    :tool="tool"
                    @delete="handleDeleteTool"
                  />
                </template>
              </ToolCard>
            </template>
          </div>
          <template #empty>
            <MkEmpty class="mt-24" />
          </template>
        </MkInfiniteScroll>
      </div>

      <component
        :is="Footer"
        v-if="batchSelectionMode"
        v-model:batch-selection="selectedToolIds"
        :batch-values="toolIds"
        @batch-cancel="cancelBatchSelection"
      >
        <template #footer-batch-actions>
          <el-button v-if="perm.tool.workspace.batchMove()" type="primary" plain :disabled="!selectedToolCount" @click="handleOpenBatchMove">
            {{ t('folder.actions.moveTo') }}
          </el-button>
          <el-button v-if="perm.tool.workspace.batchDelete()" type="danger" plain :disabled="!selectedToolCount" @click="handleBatchDelete">
            {{ t('common.actions.delete') }}
          </el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>

  <MoveToDialog ref="batchMoveToDialogRef" :loading="toolOperationLoading" :source="RESOURCE_TYPE.TOOL" @submit="handleBatchMove" />
  <EditToolForm ref="editToolFormRef" :api="ToolApi" @update="handleToolUpdate" />
</template>
