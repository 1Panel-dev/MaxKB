<script setup lang="ts">
import { computed, ref, useTemplateRef, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Box, Coin, Connection, Folder, MagicStick } from '@element-plus/icons-vue'
import { ElMessageBox, ElTree, type TreeKey, type TreeNodeData } from 'element-plus'
import type { ToolFolder, ToolType, WorkspaceTool } from '@/api/types'
import ToolApi from '@/api/admin/workspace/tool/tool'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import { dateFormat } from '@/utils/time'

type ToolNavigation = 'all' | 'shared' | string

const TOOL_TYPE_LABELS: Record<ToolType, string> = {
  CUSTOM: '工具',
  DATA_SOURCE: '数据源',
  INTERNAL: '内置工具',
  MCP: 'MCP',
  SKILL: 'Skills',
  WORKFLOW: '工作流',
}

const route = useRoute()
const workspaceId = computed(() => String(route.params.workspaceId))
const folderTreeRef = useTemplateRef<InstanceType<typeof ElTree>>('folderTreeRef')
const loading = ref(false)
const folderSearchKeyword = ref('')
const toolFolders = ref<ToolFolder[]>([])
const workspaceTools = ref<WorkspaceTool[]>([])
const sharedTools = ref<WorkspaceTool[]>([])
const folderTools = ref<WorkspaceTool[]>([])
const activeNavigation = ref<ToolNavigation>('all')
const activeTitle = ref('全部工具')
const selectedToolId = ref('')
const toolType = ref<ToolType | ''>('')
const sortOrder = ref<'newest' | 'oldest'>('newest')

const visibleTools = computed(() => {
  let result = workspaceTools.value
  if (activeNavigation.value === 'shared') result = sharedTools.value
  if (!['all', 'shared'].includes(activeNavigation.value)) result = folderTools.value
  if (toolType.value) result = result.filter((tool) => tool.tool_type === toolType.value)

  return [...result].sort((left, right) => {
    const leftTime = new Date(left.create_time ?? 0).getTime()
    const rightTime = new Date(right.create_time ?? 0).getTime()
    return sortOrder.value === 'newest' ? rightTime - leftTime : leftTime - rightTime
  })
})

/* 工具目录与列表 */
function loadTools() {
  loading.value = true
  return Promise.all([
    ToolApi.getToolFolderTree(workspaceId.value),
    ToolApi.getToolCatalog(workspaceId.value, { scope: 'WORKSPACE' }),
  ])
    .then(([folderTree, toolCatalog]) => {
      const rootFolder = folderTree.find(({ id }) => id === workspaceId.value) ?? folderTree[0]
      toolFolders.value = rootFolder?.children ?? folderTree
      workspaceTools.value = toolCatalog.tools.map((tool) => ({ ...tool, source: 'workspace' }))
      sharedTools.value = toolCatalog.shared_tools.map((tool) => ({ ...tool, source: 'shared' }))
      if (activeNavigation.value !== 'all' && activeNavigation.value !== 'shared') {
        const activeFolder = findFolder(toolFolders.value, activeNavigation.value)
        if (activeFolder) return loadFolderTools(activeFolder)
        handleNavigationSelect('all')
      }
    })
    .finally(() => {
      loading.value = false
    })
}

function loadFolderTools(folder: ToolFolder) {
  loading.value = true
  return ToolApi.getToolTree(workspaceId.value, {
    folder_id: folder.id,
    scope: 'WORKSPACE',
  })
    .then(({ tools }) => {
      folderTools.value = tools.map((tool) => ({ ...tool, source: 'workspace' }))
    })
    .finally(() => {
      loading.value = false
    })
}

function findFolder(folders: ToolFolder[], folderId: string): ToolFolder | undefined {
  for (const folder of folders) {
    if (folder.id === folderId) return folder
    const child = findFolder(folder.children ?? [], folderId)
    if (child) return child
  }
}

function handleNavigationSelect(navigation: 'all' | 'shared') {
  activeNavigation.value = navigation
  activeTitle.value = navigation === 'all' ? '全部工具' : '共享工具'
  selectedToolId.value = ''
  folderTreeRef.value?.setCurrentKey(null)
}

function handleFolderSelect(folder: ToolFolder) {
  activeNavigation.value = folder.id
  activeTitle.value = folder.name
  selectedToolId.value = ''
  return loadFolderTools(folder)
}

function handleToolSelect(tool: WorkspaceTool) {
  selectedToolId.value = tool.id
}

function handleFolderSearch(keyword: string) {
  folderTreeRef.value?.filter(keyword)
}

function filterFolderNode(keyword: string, folder: TreeNodeData) {
  return (
    !keyword ||
    String(folder.name ?? '')
      .toLocaleLowerCase()
      .includes(keyword.trim().toLocaleLowerCase())
  )
}

/* 文件夹维护 */
function handleCreateFolder(parentId = workspaceId.value) {
  ElMessageBox.prompt('请输入文件夹名称', '创建文件夹', {
    cancelButtonText: '取消',
    confirmButtonText: '创建',
    inputPattern: /\S+/,
    inputErrorMessage: '文件夹名称不能为空',
  })
    .then(({ value }) => {
      loading.value = true
      return ToolApi.postToolFolder(workspaceId.value, {
        name: value.trim(),
        parent_id: parentId,
      }).then(() => {
        MsgSuccess('创建成功')
        return loadTools()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleRenameFolder(folder: ToolFolder) {
  ElMessageBox.prompt('请输入新的文件夹名称', '重命名', {
    cancelButtonText: '取消',
    confirmButtonText: '保存',
    inputPattern: /\S+/,
    inputErrorMessage: '文件夹名称不能为空',
    inputValue: folder.name,
  })
    .then(({ value }) => {
      loading.value = true
      return ToolApi.putToolFolder(workspaceId.value, folder.id, {
        name: value.trim(),
      }).then(() => {
        if (activeNavigation.value === folder.id) activeTitle.value = value.trim()
        MsgSuccess('保存成功')
        return loadTools()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleDeleteFolder(folder: ToolFolder) {
  MsgConfirm(`确认删除文件夹“${folder.name}”？`, '文件夹内的工具也会被删除，请谨慎操作。')
    .then(() => {
      loading.value = true
      return ToolApi.deleteToolFolder(workspaceId.value, folder.id).then(() => {
        if (activeNavigation.value === folder.id) handleNavigationSelect('all')
        MsgSuccess('删除成功')
        return loadTools()
      })
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function formatCreatedDate(timestamp?: string) {
  return timestamp ? String(dateFormat(timestamp)) : '-'
}

function getToolCreatorText(tool: WorkspaceTool) {
  return `${tool.nick_name || '-'} 创建于 ${formatCreatedDate(tool.create_time)}`
}

function getFolderNodeKey(folder: ToolFolder): TreeKey {
  return folder.id
}

watch(workspaceId, loadTools, { immediate: true })
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

      <!-- <div class="flex shrink-0 items-center gap-2 px-4 pb-2">
        <MkSearchInput
          v-model="folderSearchKeyword"
          class="min-w-0 flex-1"
          @input="handleFolderSearch"
        />
        <el-button aria-label="筛选文件夹" class="shrink-0 px-2!">
          <MkIcon name="icon_moments-categories_outlined" />
        </el-button>
      </div>

      <el-scrollbar class="min-h-0 flex-1 px-4 pb-4">
        <button
          type="button"
          class="tool-navigation-item"
          :class="{ active: activeNavigation === 'shared' }"
          @click="handleNavigationSelect('shared')"
        >
          <MkIcon name="icon_assigned_outlined" :size="20" />
          <span>共享工具</span>
        </button>

        <el-divider class="my-2!" />

        <button
          type="button"
          class="tool-navigation-item"
          :class="{ active: activeNavigation === 'all' }"
          @click="handleNavigationSelect('all')"
        >
          <MkIcon name="icon_moments-categories_outlined" :size="20" />
          <span>全部工具</span>
        </button>

        <el-tree
          ref="folderTreeRef"
          class="tool-folder-tree mt-1"
          :data="toolFolders"
          :expand-on-click-node="false"
          :filter-node-method="filterFolderNode"
          :get-node-key="getFolderNodeKey"
          highlight-current
          node-key="id"
          @node-click="handleFolderSelect"
        >
          <template #default="{ data: folder }">
            <span class="group flex min-w-0 flex-1 items-center gap-2">
              <MkIcon :icon="Folder" class="text-warning!" :size="20" />
              <span class="min-w-0 flex-1 truncate" :title="String(folder.name ?? '')">
                {{ folder.name }}
              </span>
              <MkDropdown trigger="click" :teleported="false">
                <el-button
                  text
                  class="pointer-events-none -mr-1 opacity-0 group-hover:pointer-events-auto group-hover:opacity-100"
                  @click.stop
                >
                  <MkIcon name="icon_more_outlined" />
                </el-button>
                <template #dropdown>
                  <MkDropdownMenu>
                    <MkDropdownItem @click="handleRenameFolder(folder)">
                      <template #icon><MkIcon name="icon_edit_outlined" /></template>
                      重命名
                    </MkDropdownItem>
                    <MkDropdownItem @click="handleCreateFolder(folder.id)">
                      <template #icon><MkIcon name="icon_add_outlined" /></template>
                      创建子文件夹
                    </MkDropdownItem>
                    <MkDropdownItem divided @click="handleDeleteFolder(folder)">
                      <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
                      删除
                    </MkDropdownItem>
                  </MkDropdownMenu>
                </template>
              </MkDropdown>
            </span>
          </template>
        </el-tree>
      </el-scrollbar> -->
    </template>

    <!-- <template #default="{ Header }">
      <component :is="Header">
        <div class="flex min-w-0 items-center gap-4">
          <h4 class="truncate" :title="activeTitle">{{ activeTitle }}</h4>
          <el-divider direction="vertical" />
          <el-select v-model="toolType" class="w-32" aria-label="工具类型">
            <el-option label="全部" value="" />
            <el-option label="工具" value="CUSTOM" />
            <el-option label="Skills" value="SKILL" />
            <el-option label="工作流" value="WORKFLOW" />
            <el-option label="MCP" value="MCP" />
            <el-option label="数据源" value="DATA_SOURCE" />
          </el-select>
        </div>
        <el-select v-model="sortOrder" class="w-32" aria-label="工具排序">
          <el-option label="最新创建" value="newest" />
          <el-option label="最早创建" value="oldest" />
        </el-select>
      </component>

      <div v-if="visibleTools.length" class="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <article
          v-for="tool in visibleTools"
          :key="`${tool.source}:${tool.id}`"
          class="tool-card"
          :class="{ active: selectedToolId === tool.id }"
          @click="handleToolSelect(tool)"
        >
          <header class="flex min-w-0 items-start gap-3">
            <img
              v-if="tool.icon"
              :src="tool.icon"
              :alt="tool.name"
              class="h-8 w-8 shrink-0 rounded-lg object-cover"
            />
            <span v-else class="tool-type-icon" :class="`type-${tool.tool_type.toLowerCase()}`">
              <span v-if="tool.tool_type === 'MCP'" class="text-xs font-semibold">MCP</span>
              <MkIcon v-else-if="tool.tool_type === 'WORKFLOW'" :icon="Connection" :size="20" />
              <MkIcon v-else-if="tool.tool_type === 'SKILL'" :icon="MagicStick" :size="20" />
              <MkIcon v-else-if="tool.tool_type === 'DATA_SOURCE'" :icon="Coin" :size="20" />
              <MkIcon v-else :icon="Box" :size="20" />
            </span>
            <div class="min-w-0 flex-1">
              <div class="flex items-center gap-2">
                <h5 class="truncate" :title="tool.name">{{ tool.name }}</h5>
                <el-tag v-if="tool.version" size="small" type="info" effect="plain">
                  {{ tool.version }}
                </el-tag>
              </div>
              <p class="truncate text-N600" :title="getToolCreatorText(tool)">
                {{ getToolCreatorText(tool) }}
              </p>
            </div>
          </header>

          <p
            class="mt-7 line-clamp-2 min-h-11 text-N600"
            :title="tool.desc || TOOL_TYPE_LABELS[tool.tool_type]"
          >
            {{ tool.desc || TOOL_TYPE_LABELS[tool.tool_type] }}
          </p>

          <footer class="mt-auto pt-7 text-N600">
            <MkStatusLabel :active="tool.is_active" />
          </footer>
        </article>
      </div>
      <MkEmpty v-else class="mt-24" />
    </template> -->
  </MkViewLayout>
</template>

<style scoped lang="scss"></style>
