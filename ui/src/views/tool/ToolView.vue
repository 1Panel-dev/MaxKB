<script setup lang="ts">
import { onMounted, computed, ref, useTemplateRef } from 'vue'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SharedApi from '@/api/admin/workspace/shared'
import ToolStoreApi from '@/api/admin/tool-store.ts'
import type {
  Dict,
  FolderItem,
  OptionItem,
  ToolItem,
  ToolStoreResponse,
  ToolType,
} from '@/api/types'
import { RESOURCE_TYPE, TOOL_SCOPE } from '@/api/enums'
import { TOOL_TYPE_OPTIONS, FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from '@/components/business/folder-tree/index.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ToolCard from './tool-card/index.vue'
import {
  CopyToolAction,
  DeleteToolAction,
  EditToolAction,
  ExportToolAction,
} from './tool-card/action-dropdown'
import CreateToolDropdown from './components/CreateToolDropdown.vue'
import ToolStoreOpenButton from './tool-store/ToolStoreOpenButton.vue'

/* 当前文件夹 */

const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[RESOURCE_TYPE.TOOL].all })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder: FolderItem) {
  const folderChanged = folder.id !== currentFolder.value.id
  currentFolder.value = folder
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
  { label: '名称', value: 'name' },
  {
    label: '创建者',
    value: 'create_user',
    options: creatorOptions.value,
    remoteMethod: loadCreatorOptions,
  },
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
  const request = isShared.value ? SharedApi : ToolApi
  const folderId = isShared.value
    ? {}
    : { folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL }
  return request.getToolPage(pagination, {
    ...toolQuery.value,
    scope: TOOL_SCOPE.WORKSPACE,
    tool_type: toolType.value,
    ...folderId,
  })
}

// 加载工具商店
const storeTools = ref<ToolStoreResponse['apps']>([])

function loadStoreTools() {
  ToolStoreApi.getStoreToolList({ name: '' }).then((res) => {
    storeTools.value = res.apps
  })
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

function handleBatchDelete() {
  if (!selectedToolCount.value) return
  const toolIds = [...selectedToolIds.value]

  MsgConfirm(`是否批量删除 ${toolIds.length} 个工具？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      toolOperationLoading.value = true
      return ToolApi.putBatchDeleteTools(toolIds).then(() => {
        MsgSuccess('删除成功')
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
  <MkViewLayout class="workspace-tool-view" collapsible>
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <el-tooltip content="创建文件夹" placement="top">
          <el-button @click="handleCreateFolder" text type="primary" class="-mr-1">
            <MkIcon name="icon_add-folder_outlined" :size="18" />
          </el-button>
        </el-tooltip>
      </component>

      <FolderTree
        ref="folderTreeRef"
        :source="RESOURCE_TYPE.TOOL"
        @select="handleFolderSelect"
        draggable
      >
      </FolderTree>
    </template>

    <template #default="{ Footer, Header }">
      <component :is="Header">
        <div class="flex min-w-0 flex-1 items-center gap-4">
          <h4 class="min-w-0 truncate" :title="currentFolder?.name">{{ currentFolder?.name }}</h4>
          <el-divider direction="vertical" />
          <el-select
            v-model="toolType"
            class="w-30!"
            :empty-values="[null, undefined]"
            :value-on-clear="null"
            @change="refreshTool"
          >
            <el-option
              v-for="option in TOOL_TYPE_OPTIONS"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </div>
        <div class="flex items-center gap-3">
          <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
          <template v-if="!isShared">
            <span>
              <el-button
                v-if="toolsData.length"
                :type="batchSelectionMode ? 'primary' : undefined"
                plain
                @click="toggleBatchSelection"
              >
                <MkIcon name="icon_Batch_outlined" />
                <span>{{ batchSelectionMode ? '取消选择' : '批量选择' }}</span>
              </el-button>
            </span>

            <template v-if="!batchSelectionMode">
              <ToolStoreOpenButton :folder-id="currentFolder.id" @refresh="refreshTool" />
              <CreateToolDropdown :folder-id="currentFolder.id" @refresh="refreshTool" />
            </template>
          </template>
        </div>
      </component>
      <div v-loading="toolOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="toolsData" :load="loadToolsPage">
          <div v-if="toolsData.length" class="mk-resource-card-grid">
            <template v-for="tool in toolsData" :key="tool.id">
              <ToolCard
                v-model:loading="toolOperationLoading"
                :api="ToolApi"
                :disabled="isShared"
                :selectable="batchSelectionMode"
                :selected="selectedToolIds.includes(tool.id)"
                :shared="isShared"
                :store-tools="storeTools"
                :tool="tool"
                @selected="handleToolSelect(tool.id, $event)"
                @update="handleToolUpdate"
              >
                <template #action-dropdown>
                  <EditToolAction
                    label="编辑"
                    :api="ToolApi"
                    :store-tools="storeTools"
                    :tool="tool"
                    @refresh="refreshTool"
                  />
                  <CopyToolAction label="复制" :tool="tool" />
                  <ExportToolAction
                    v-model:loading="toolOperationLoading"
                    label="导出"
                    :api="ToolApi"
                    :tool="tool"
                  />
                  <DeleteToolAction
                    v-model:loading="toolOperationLoading"
                    label="删除"
                    :api="ToolApi"
                    :tool="tool"
                    @delete="handleDeleteTool"
                  />
                </template>
              </ToolCard>
            </template>
          </div>
          <MkEmpty v-else class="mt-24" />
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
          <el-button type="danger" plain :disabled="!selectedToolCount" @click="handleBatchDelete">
            删除
          </el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>
</template>
