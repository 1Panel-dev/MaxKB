<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import ToolStoreApi from '@/api/admin/tool-store'
import ToolApi from '@/api/admin/workspace/tool/tool'
import WorkspaceToolStoreApi from '@/api/admin/workspace/tool/store'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolStoreItem, ToolStoreTag, ToolType } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import { resetUrl } from '@/utils/common'
import ToolStoreCard from './ToolStoreCard.vue'
import ToolStoreDetailDrawer from './ToolStoreDetailDrawer.vue'
import AddStoreToolDialog from './AddStoreToolDialog.vue'

defineOptions({ name: 'ToolStoreDialog' })

const emit = defineEmits<{
  refresh: []
}>()

interface ToolStoreCategory {
  id: string
  title: string
  tools: ToolStoreItem[]
}

const DEFAULT_CATEGORY_TITLES: Record<string, string> = {
  database_search: '数据库查询',
  other: '其他',
  web_search: '联网搜索',
}

const visible = ref(false)
const loading = ref(false)
const addingToolId = ref<string>()
const folderId = ref('default')
const searchKeyword = ref('')
const storeTools = ref<ToolStoreItem[]>([])
const storeTags = ref<ToolStoreTag[]>([])

const categoryTitles = computed(() => {
  return storeTags.value.reduce<Record<string, string>>(
    (titles, tag) => ({ ...titles, [tag.key]: tag.name }),
    { ...DEFAULT_CATEGORY_TITLES },
  )
})

const toolStoreCategories = computed<ToolStoreCategory[]>(() => {
  const categoryMap = new Map<string, ToolStoreItem[]>()
  storeTools.value.forEach((tool) => {
    const categoryId = tool.label || 'other'
    categoryMap.set(categoryId, [...(categoryMap.get(categoryId) ?? []), tool])
  })

  return Array.from(categoryMap, ([id, tools]) => ({
    id,
    title: categoryTitles.value[id] ?? id,
    tools,
  }))
})

function getStoreToolType(label?: string | null): ToolType {
  if (label === 'data_source') return TOOL_TYPE.DATA_SOURCE
  if (label === 'skill') return TOOL_TYPE.SKILL
  if (label === 'workflow_template') return TOOL_TYPE.WORKFLOW
  return TOOL_TYPE.CUSTOM
}

function normalizeInternalTool(tool: ToolItem): ToolStoreItem {
  return {
    desc: tool.desc,
    icon: tool.icon,
    id: tool.id,
    label: tool.label,
    name: tool.name,
    source: 'internal',
    tool_type: TOOL_TYPE.INTERNAL,
    version: tool.version,
  }
}

function loadStoreTools() {
  loading.value = true
  storeTools.value = []
  const query = searchKeyword.value.trim() ? { name: searchKeyword.value.trim() } : undefined

  Promise.all([ToolStoreApi.getInternalToolList(query), ToolStoreApi.getStoreToolList(query)])
    .then(([internalTools, storeResponse]) => {
      const appStoreTools: ToolStoreItem[] = storeResponse.apps.map((tool) => ({
        ...tool,
        desc: tool.description ?? tool.desc,
        source: 'store',
        tool_type: getStoreToolType(tool.label),
      }))
      storeTags.value = storeResponse.additionalProperties.tags
      storeTools.value = [...internalTools.map(normalizeInternalTool), ...appStoreTools]
    })
    .finally(() => {
      loading.value = false
    })
}

function open(targetFolderId: string) {
  folderId.value = targetFolderId || 'default'
  searchKeyword.value = ''
  storeTools.value = []
  visible.value = true
  loadStoreTools()
}

/* 商店分类与详情 */
function handleCategorySelect(categoryId: string) {
  document.getElementById(`tool-store-category-${categoryId}`)?.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

const detailDrawerRef =
  useTemplateRef<InstanceType<typeof ToolStoreDetailDrawer>>('detailDrawerRef')

function handleOpenDetail(tool: ToolStoreItem) {
  if (tool.source !== 'internal' || !tool.icon?.includes('icon.png')) {
    detailDrawerRef.value?.open(tool)
    return
  }

  const detailUrl = resetUrl(tool.icon.replace('icon.png', 'detail.md'))
  fetch(detailUrl)
    .then((response) => (response.ok ? response.text() : Promise.reject(response)))
    .then((content) => detailDrawerRef.value?.open(tool, content))
    .catch(() => detailDrawerRef.value?.open(tool))
}

/* 添加商店工具 */
const addToolDialogRef = useTemplateRef<InstanceType<typeof AddStoreToolDialog>>('addToolDialogRef')

function handleOpenAddTool(tool: ToolStoreItem) {
  addToolDialogRef.value?.open(tool)
}

function handleAddTool(tool: ToolStoreItem, name: string) {
  addingToolId.value = tool.id
  const commonPayload = { folder_id: folderId.value, name }
  let request: Promise<unknown>

  if (tool.source === 'internal') {
    request = WorkspaceToolStoreApi.postInternalTool(tool.id, commonPayload)
  } else if (tool.tool_type === TOOL_TYPE.WORKFLOW) {
    request = ToolApi.postTool({
      ...commonPayload,
      code: '{}',
      tool_type: TOOL_TYPE.WORKFLOW,
      work_flow_template: tool,
    })
  } else {
    request = WorkspaceToolStoreApi.postStoreTool(tool.id, {
      ...commonPayload,
      download_callback_url: tool.downloadCallbackUrl ?? '',
      download_url: tool.downloadUrl ?? '',
      icon: tool.icon ?? '',
      label: tool.label ?? '',
      versions: tool.versions ?? [],
    })
  }

  request
    .then(() => {
      MsgSuccess('添加成功')
      visible.value = false
      emit('refresh')
    })
    .finally(() => {
      addingToolId.value = undefined
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog
    v-model="visible"
    class="tool-store-dialog"
    content-class="p-0!"
    title="工具商店"
    width="1200"
  >
    <div class="tool-store-layout flex min-h-0">
      <aside v-if="!searchKeyword" class="w-52 shrink-0 border-r border-N200 bg-N100 p-3">
        <el-scrollbar>
          <el-button
            v-for="category in toolStoreCategories"
            :key="category.id"
            class="mb-1 w-full justify-start!"
            text
            @click="handleCategorySelect(category.id)"
          >
            {{ category.title }}
          </el-button>
        </el-scrollbar>
      </aside>

      <main class="flex min-w-0 flex-1 flex-col">
        <div class="flex justify-end border-b border-N200 px-6 py-3">
          <MkSearchInput
            v-model="searchKeyword"
            class="w-70!"
            placeholder="搜索工具"
            @change="loadStoreTools"
            @keyup.enter="loadStoreTools"
          />
        </div>

        <el-scrollbar v-loading="loading" class="min-h-0 flex-1">
          <div class="p-6">
            <template v-if="storeTools.length">
              <div v-if="searchKeyword" class="mb-4">
                找到 <strong class="text-primary">{{ storeTools.length }}</strong> 个相关工具
              </div>
              <div v-if="searchKeyword" class="mk-resource-card-grid">
                <ToolStoreCard
                  v-for="tool in storeTools"
                  :key="`${tool.source}-${tool.id}`"
                  :category-title="categoryTitles[tool.label || 'other'] ?? tool.label ?? '其他'"
                  :loading="addingToolId === tool.id"
                  :tool="tool"
                  @add="handleOpenAddTool(tool)"
                  @detail="handleOpenDetail(tool)"
                />
              </div>
              <template v-else>
                <section
                  v-for="category in toolStoreCategories"
                  :id="`tool-store-category-${category.id}`"
                  :key="category.id"
                  class="mb-8 scroll-mt-4"
                >
                  <h4 class="mk-title-decoration mb-4">{{ category.title }}</h4>
                  <div class="mk-resource-card-grid">
                    <ToolStoreCard
                      v-for="tool in category.tools"
                      :key="`${tool.source}-${tool.id}`"
                      :category-title="category.title"
                      :loading="addingToolId === tool.id"
                      :tool="tool"
                      @add="handleOpenAddTool(tool)"
                      @detail="handleOpenDetail(tool)"
                    />
                  </div>
                </section>
              </template>
            </template>
            <MkEmpty v-else class="mt-24" />
          </div>
        </el-scrollbar>
      </main>
    </div>
  </MkDialog>

  <ToolStoreDetailDrawer ref="detailDrawerRef" @add="handleOpenAddTool" />
  <AddStoreToolDialog ref="addToolDialogRef" @submit="handleAddTool" />
</template>

<style scoped lang="scss">
.tool-store-layout {
  height: min(680px, calc(100vh - 220px));
}
</style>
