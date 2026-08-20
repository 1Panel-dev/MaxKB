<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { FOLDER_SOURCE, TOOL_SCOPE } from '@/api/enums'
import type { OptionItem, RequestParams, ToolType, WorkspaceTool, FolderItem } from '@/api/types'
import CommonApi from '@/api/admin/workspace/common'
import ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE_OPTIONS } from '@/constants'
import { FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants/folder'
import FolderTree from '@/components/business/folder-tree/index.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ToolCard from './components/ToolCard.vue'

/* 当前文件夹 */
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[FOLDER_SOURCE.TOOL].all })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder: FolderItem) {
  currentFolder.value = folder
  selectedToolId.value = ''
  resetAndLoadTools()
}

/* 工具查询搜索列表 */
const loading = ref(false)
const loadingMore = ref(false)
const paginationConfig = ref({
  currentPage: 1,
  pageSize: 20,
  total: 0,
})
const toolsData = ref<WorkspaceTool[]>([])
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
  return CommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: RequestParams) {
  toolQuery.value = query
  resetAndLoadTools()
}

const toolType = ref<ToolType | ''>('')
let latestToolsRequest = 0

function handleToolTypeChange() {
  selectedToolId.value = ''
  resetAndLoadTools()
}

function loadToolsPage(currentPage = 1) {
  const append = currentPage > 1
  const requestId = ++latestToolsRequest
  if (append) {
    loadingMore.value = true
  } else {
    loading.value = true
    loadingMore.value = false
  }

  return ToolApi.getToolPage(
    { currentPage, pageSize: paginationConfig.value.pageSize },
    {
      ...toolQuery.value,
      scope: TOOL_SCOPE.WORKSPACE,
      folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL,
      tool_type: toolType.value,
    },
  )
    .then((tools) => {
      if (requestId !== latestToolsRequest) return

      toolsData.value = append ? [...toolsData.value, ...tools.records] : tools.records
      paginationConfig.value.currentPage = tools.current
      paginationConfig.value.pageSize = tools.size
      paginationConfig.value.total = tools.total
    })
    .finally(() => {
      if (requestId !== latestToolsRequest) return

      loading.value = false
      loadingMore.value = false
    })
}

function resetAndLoadTools() {
  paginationConfig.value.currentPage = 1
  paginationConfig.value.total = 0
  toolsData.value = []
  return loadToolsPage()
}

const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
const selectedToolId = ref('')

function handleToolSelect(tool: WorkspaceTool) {
  selectedToolId.value = tool.id
}

function handleCreateFolder() {
  folderTreeRef.value?.openCreate()
}

/* 工具维护 */
function handleToolStatusChange(tool: WorkspaceTool, active: boolean) {
  loading.value = true
  return ToolApi.putTool(tool.id, { is_active: active })
    .then(() => {
      tool.is_active = active
      MsgSuccess(active ? '启用成功' : '禁用成功')
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDeleteTool(tool: WorkspaceTool) {
  MsgConfirm(`确认删除工具“${tool.name}”？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      loading.value = true
      return ToolApi.deleteTool(tool.id).then(() => {
        MsgSuccess('删除成功')
        return loadToolsPage()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

onMounted(() => {
  loadToolsPage()
})
</script>

<template>
  <MkViewLayout class="workspace-tool-view">
    <template #aside="{ title, Header }">
      <component :is="Header">
        <h4>{{ title }}</h4>
        <el-tooltip content="创建文件夹" placement="top">
          <el-button text type="primary" class="-mr-1" @click="handleCreateFolder()">
            <MkIcon name="icon_add_outlined" :size="18" />
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
            @change="handleToolTypeChange"
          >
            <el-option
              v-for="option in TOOL_TYPE_OPTIONS"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </div>
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
      </component>
      <div v-loading="loading">
        <el-row v-if="toolsData.length" :gutter="16" class="gap-y-4">
          <el-col
            v-for="tool in toolsData"
            :key="tool.id"
            :xs="24"
            :sm="24"
            :md="12"
            :lg="8"
            :xl="8"
          >
            <ToolCard
              :selected="selectedToolId === tool.id"
              :shared="isShared"
              :tool="tool"
              @delete="handleDeleteTool"
              @select="handleToolSelect"
              @status-change="handleToolStatusChange"
            />
          </el-col>
        </el-row>
        <MkEmpty v-else-if="!loading" class="mt-24" />
        <MkLoadMore
          v-if="toolsData.length"
          :loading="loadingMore"
          :pagination-config="paginationConfig"
          @load="loadToolsPage"
        />
      </div>
    </template>
  </MkViewLayout>
</template>
