<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import ToolApi from '@/api/admin/workspace/tool/tool'
import SharedApi from '@/api/admin/workspace/shared'
import type { OptionItem, RequestParams, ToolType, ToolItem, FolderItem } from '@/api/types'
import { FOLDER_SOURCE, TOOL_SCOPE } from '@/api/enums'
import { TOOL_TYPE_OPTIONS, FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from '@/components/business/folder-tree/index.vue'

import ToolCard from './components/ToolCard.vue'
import ToolCreateDropdown from './components/ToolCreateDropdown.vue'

/* 当前文件夹 */

const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[FOLDER_SOURCE.TOOL].all })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder: FolderItem) {
  const folderChanged = folder.id !== currentFolder.value.id
  currentFolder.value = folder
  if (folderChanged) refreshTool()
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
const toolQuery = ref<RequestParams>()
function loadCreatorOptions(keyword: string) {
  const requestApi = isShared.value ? CommonSystemApi : CommonApi
  return requestApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: RequestParams) {
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

/* 工具维护 */
const toolOperationLoading = ref(false)

function refreshTool() {
  infiniteScrollRef.value?.reset()
}

function handleToolUpdate(tool: ToolItem) {
  const toolIndex = toolsData.value.findIndex((item) => item.id === tool.id)
  if (toolIndex >= 0) toolsData.value.splice(toolIndex, 1, tool)
}

function handleDeleteTool(toolId: string) {
  const toolIndex = toolsData.value.findIndex((item) => item.id === toolId)
  if (toolIndex >= 0) toolsData.value.splice(toolIndex, 1)
}
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
        :source="FOLDER_SOURCE.TOOL"
        @select="handleFolderSelect"
        draggable
      >
      </FolderTree>
    </template>

    <template #default="{ Header }">
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
          <ToolCreateDropdown
            v-if="!isShared"
            :folder-id="currentFolder.id"
            @refresh="refreshTool"
          />
        </div>
      </component>
      <div v-loading="toolOperationLoading" class="min-h-0 flex-1">
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="toolsData" :load="loadToolsPage">
          <div v-if="toolsData.length" class="mk-resource-card-grid">
            <template v-for="tool in toolsData" :key="tool.id">
              <ToolCard
                v-model:loading="toolOperationLoading"
                :shared="isShared"
                :tool="tool"
                @delete="handleDeleteTool"
                @update="handleToolUpdate"
              />
            </template>
          </div>
          <MkEmpty v-else class="mt-24" />
        </MkInfiniteScroll>
      </div>
    </template>
  </MkViewLayout>
</template>
