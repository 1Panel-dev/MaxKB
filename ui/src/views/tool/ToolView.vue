<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import type {
  OptionItem,
  RequestParams,
  ToolListQuery,
  ToolType,
  WorkspaceFolder,
  WorkspaceTool,
} from '@/api/types'
import { FOLDER_SOURCE, TOOL_SCOPE, TOOL_TYPE } from '@/api/types'
import CommonApi from '@/api/admin/workspace/common'
import ToolApi from '@/api/admin/workspace/tool/tool'
import FolderTree from '@/components/business/folder-tree/index.vue'
import MkListItem from '@/components/mk-search-list/mk-list-item.vue'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import ToolCard from './components/ToolCard.vue'

type ToolNavigation = 'all' | 'shared' | string

const TOOL_TYPE_OPTIONS: OptionItem<ToolType | ''>[] = [
  { label: '全部', value: '' },
  { label: '工具', value: TOOL_TYPE.CUSTOM },
  { label: 'Skills', value: TOOL_TYPE.SKILL },
  { label: '工作流', value: TOOL_TYPE.WORKFLOW },
  { label: 'MCP', value: TOOL_TYPE.MCP },
  { label: '数据源', value: TOOL_TYPE.DATA_SOURCE },
]

const route = useRoute()
const workspaceId = computed(() => String(route.params.workspaceId))
const folderTreeRef = useTemplateRef<InstanceType<typeof FolderTree>>('folderTreeRef')
const loading = ref(false)
const visibleTools = ref<WorkspaceTool[]>([])
const activeNavigation = ref<ToolNavigation>('shared')
const activeTitle = ref('共享工具')
const selectedToolId = ref('')
const toolType = ref<ToolType | ''>('')
const toolQuery = ref<RequestParams>()
const creatorOptions = ref<OptionItem<string>[]>([])

const isShared = computed(() => activeNavigation.value === 'shared')
const searchFields = computed(() => [
  { label: '名称', value: 'name' },
  {
    label: '创建者',
    value: 'create_user',
    options: creatorOptions.value,
    remoteMethod: loadCreatorOptions,
  },
])

function getToolListQuery(): ToolListQuery {
  return {
    ...toolQuery.value,
    scope: TOOL_SCOPE.WORKSPACE,
    ...(toolType.value ? { tool_type: toolType.value } : {}),
  }
}

/* 工具列表 */
function loadVisibleTools() {
  loading.value = true
  const query = getToolListQuery()

  const request =
    activeNavigation.value === 'all' || isShared.value
      ? ToolApi.getToolCatalog(workspaceId.value, query).then((catalog) =>
          isShared.value ? catalog.shared_tools : catalog.tools,
        )
      : ToolApi.getToolTree(workspaceId.value, {
          ...query,
          folder_id: activeNavigation.value,
        }).then(({ tools }) => tools)

  return request
    .then((tools) => {
      visibleTools.value = tools.map((tool) => ({
        ...tool,
        source: isShared.value ? 'shared' : 'workspace',
      }))
    })
    .finally(() => {
      loading.value = false
    })
}

function handleNavigationSelect(navigation: 'all' | 'shared' | WorkspaceFolder) {
  selectedToolId.value = ''
  if (typeof navigation === 'string') {
    activeNavigation.value = navigation
    activeTitle.value = navigation === 'all' ? '全部工具' : '共享工具'
  } else {
    activeNavigation.value = navigation.id
    activeTitle.value = navigation.name
  }
  loadVisibleTools()
}

function handleCreateFolder() {
  folderTreeRef.value?.openCreate()
}

function handleFolderDeleted(_folder: WorkspaceFolder, selectionAffected: boolean) {
  if (selectionAffected) handleNavigationSelect('all')
}

function handleFolderUpdated(folder: WorkspaceFolder) {
  if (activeNavigation.value === folder.id) activeTitle.value = folder.name
}

function handleToolSelect(tool: WorkspaceTool) {
  selectedToolId.value = tool.id
}

/* 搜索与筛选 */
function loadCreatorOptions(keyword: string) {
  return CommonApi.getAllUsers(
    workspaceId.value,
    keyword ? { nick_name: keyword } : undefined,
  ).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

function handleSearchChange(query?: RequestParams) {
  toolQuery.value = query
  loadVisibleTools()
}

function handleToolTypeChange() {
  selectedToolId.value = ''
  loadVisibleTools()
}

/* 工具维护 */
function handleToolStatusChange(tool: WorkspaceTool, active: boolean) {
  loading.value = true
  return ToolApi.putTool(workspaceId.value, tool.id, { is_active: active })
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
      return ToolApi.deleteTool(workspaceId.value, tool.id).then(() => {
        MsgSuccess('删除成功')
        return loadVisibleTools()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleWorkspaceChange() {
  activeNavigation.value = 'shared'
  activeTitle.value = '共享工具'
  selectedToolId.value = ''
  loadVisibleTools()
}

watch(workspaceId, handleWorkspaceChange, { immediate: true })
</script>

<template>
  <MkViewLayout class="workspace-tool-view" :loading="loading" title="工具">
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
        v-model="activeNavigation"
        :source="FOLDER_SOURCE.TOOL"
        :workspace-id="workspaceId"
        @deleted="handleFolderDeleted"
        @select="handleNavigationSelect"
        @updated="handleFolderUpdated"
      >
        <template #beforeTree>
          <div class="px-4">
            <MkListItem
              :active="activeNavigation === 'shared'"
              @click="handleNavigationSelect('shared')"
            >
              <MkIcon
                :name="
                  activeNavigation === 'shared'
                    ? 'icon_folder-share_filled'
                    : 'icon_folder_outlined'
                "
                :size="18"
                class="mr-2"
              />
              <span>共享工具</span>
            </MkListItem>

            <el-divider class="my-1!" />

            <MkListItem :active="activeNavigation === 'all'" @click="handleNavigationSelect('all')">
              <MkIcon
                :name="activeNavigation === 'all' ? 'icon_card_filled' : 'icon_card_outlined'"
                :size="18"
                class="mr-2"
              />
              <span>全部工具</span>
            </MkListItem>
          </div>
        </template>
      </FolderTree>
    </template>

    <template #default="{ Header }">
      <component :is="Header">
        <div class="flex min-w-0 items-center gap-4">
          <h4 class="truncate" :title="activeTitle">{{ activeTitle }}</h4>
          <el-select
            v-model="toolType"
            aria-label="工具类型"
            class="w-32"
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

      <el-row v-if="visibleTools.length" :gutter="16" class="gap-y-4">
        <el-col
          v-for="tool in visibleTools"
          :key="`${tool.source}:${tool.id}`"
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
      <MkEmpty v-else class="mt-24" />
    </template>
  </MkViewLayout>
</template>
