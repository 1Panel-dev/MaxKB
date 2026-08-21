<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'

import CommonApi from '@/api/admin/workspace/common'
import ToolApi from '@/api/admin/workspace/tool/tool'
import type { OptionItem, RequestParams, ToolType, ToolItem, FolderItem } from '@/api/types'
import { FOLDER_SOURCE, TOOL_SCOPE } from '@/api/enums'
import { TOOL_TYPE_OPTIONS, FOLDER_ENTRIES, FOLDER_ENTRY_ID } from '@/constants'
import FolderTree from '@/components/business/folder-tree/index.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ToolCard from './components/ToolCard.vue'

/* 当前文件夹 */
const currentFolder = ref<FolderItem>({ ...FOLDER_ENTRIES[FOLDER_SOURCE.TOOL].all })
const isShared = computed(() => currentFolder.value.id === FOLDER_ENTRY_ID.SHARED)

function handleFolderSelect(folder: FolderItem) {
  currentFolder.value = folder
  selectedToolId.value = ''
  infiniteScrollRef.value?.reset()
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
  return CommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: RequestParams) {
  toolQuery.value = query
  infiniteScrollRef.value?.reset()
}

const toolType = ref<ToolType | ''>('')

function handleToolTypeChange() {
  selectedToolId.value = ''
  infiniteScrollRef.value?.reset()
}

function loadToolsPage(pagination: { currentPage: number; pageSize: number }) {
  return ToolApi.getToolPage(pagination, {
    ...toolQuery.value,
    scope: TOOL_SCOPE.WORKSPACE,
    folder_id: currentFolder.value.id || FOLDER_ENTRY_ID.ALL,
    tool_type: toolType.value,
  })
}

// 文件夹
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
const selectedToolId = ref('')

function handleToolSelect(tool: ToolItem) {
  selectedToolId.value = tool.id
}

function handleCreateFolder() {
  folderTreeRef.value?.openCreate()
}

/* 工具维护 */
const loading = ref(false)
function handleToolStatusChange(tool: ToolItem, active: boolean) {
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

function handleDeleteTool(tool: ToolItem) {
  MsgConfirm(`确认删除工具“${tool.name}”？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      loading.value = true
      return ToolApi.deleteTool(tool.id).then(() => {
        MsgSuccess('删除成功')
        return infiniteScrollRef.value?.reset()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <MkViewLayout class="workspace-tool-view" collapsible>
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
        <MkInfiniteScroll ref="infiniteScrollRef" v-model="toolsData" :load="loadToolsPage">
          <div v-if="toolsData.length" class="mk-resource-card-grid">
            <template v-for="tool in toolsData" :key="tool.id">
              <ToolCard :shared="isShared" :tool="tool" />
            </template>
          </div>
          <MkEmpty v-else class="mt-24" />
        </MkInfiniteScroll>
      </div>
    </template>
  </MkViewLayout>
</template>
