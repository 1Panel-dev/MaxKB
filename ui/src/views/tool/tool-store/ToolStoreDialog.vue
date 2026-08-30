<script setup lang="ts">
import { computed, nextTick, ref, shallowRef, useTemplateRef } from 'vue'
import ToolStoreApi from '@/api/admin/tool-store'
import { TOOL_TYPE } from '@/api/enums'
import type { ToolItem, ToolStoreItem, ToolStoreTag, ToolType } from '@/api/types'
import ToolStoreCard from './component/ToolStoreCard.vue'

defineOptions({ name: 'ToolStoreDialog' })

const emit = defineEmits<{ refresh: [] }>()

interface ToolStoreCategory {
  id: string
  title: string
  tools: ToolStoreItem[]
}

const DEFAULT_CATEGORY_TITLES: Record<string, string> = { database_search: '数据库查询', other: '其他', web_search: '联网搜索' }
const DEFAULT_CATEGORY_IDS = ['web_search', 'database_search']
const TOOL_STORE_CATEGORY_ANCHOR_PREFIX = '#tool-store-category-'

const visible = ref(false)
const loading = ref(false)
const activeCategoryId = ref('')
const appliedSearchKeyword = ref('')
const folderId = ref('default')
const searchKeyword = ref('')
const storeTools = ref<ToolStoreItem[]>([])
const storeTags = ref<ToolStoreTag[]>([])
const hasSearchKeyword = computed(() => Boolean(appliedSearchKeyword.value))
let storeToolsLoadSequence = 0

const categoryTitles = computed(() => {
  return storeTags.value.reduce<Record<string, string>>((titles, tag) => ({ ...titles, [tag.key]: tag.name }), { ...DEFAULT_CATEGORY_TITLES })
})

const toolStoreCategories = computed<ToolStoreCategory[]>(() => {
  const categoryMap = new Map<string, ToolStoreItem[]>()
  storeTools.value.forEach((tool) => {
    const categoryId = tool.label || 'other'
    categoryMap.set(categoryId, [...(categoryMap.get(categoryId) ?? []), tool])
  })

  const categoryIds = [...DEFAULT_CATEGORY_IDS, ...storeTags.value.map(({ key }) => key), ...Array.from(categoryMap.keys())].filter(
    (categoryId, index, categories) => categories.indexOf(categoryId) === index,
  )

  return categoryIds.flatMap((id) => {
    const tools = categoryMap.get(id)
    return tools?.length ? [{ id, title: categoryTitles.value[id] ?? id, tools }] : []
  })
})

function getStoreToolType(label?: string | null): ToolType {
  if (label === 'data_source') return TOOL_TYPE.DATA_SOURCE
  if (label === 'skill') return TOOL_TYPE.SKILL
  if (label === 'workflow_template') return TOOL_TYPE.WORKFLOW
  return TOOL_TYPE.CUSTOM
}

function normalizeInternalTool(tool: ToolItem): ToolStoreItem {
  return { desc: tool.desc, icon: tool.icon, id: tool.id, label: tool.label, name: tool.name, source: 'internal', tool_type: TOOL_TYPE.INTERNAL, version: tool.version }
}

function loadStoreTools() {
  const currentLoadSequence = ++storeToolsLoadSequence
  loading.value = true
  storeTools.value = []
  appliedSearchKeyword.value = searchKeyword.value.trim()
  const query = appliedSearchKeyword.value ? { name: appliedSearchKeyword.value } : undefined

  Promise.all([ToolStoreApi.getInternalToolList(query), ToolStoreApi.getStoreToolList(query)])
    .then(([internalTools, storeResponse]) => {
      if (currentLoadSequence !== storeToolsLoadSequence) return

      const appStoreTools: ToolStoreItem[] = storeResponse.apps.map((tool) => ({
        ...tool,
        desc: tool.description ?? tool.desc,
        source: 'store',
        tool_type: getStoreToolType(tool.label),
      }))
      storeTags.value = storeResponse.additionalProperties.tags
      storeTools.value = [...internalTools.map(normalizeInternalTool), ...appStoreTools]
      return nextTick(() => {
        contentScrollContainer.value = storeLayoutRef.value?.getScrollContainer()
        activeCategoryId.value = toolStoreCategories.value[0]?.id ?? ''
        storeLayoutRef.value?.setScrollTop(0)
      })
    })
    .finally(() => {
      if (currentLoadSequence === storeToolsLoadSequence) loading.value = false
    })
}

function open(targetFolderId: string) {
  folderId.value = targetFolderId || 'default'
  searchKeyword.value = ''
  appliedSearchKeyword.value = ''
  storeTools.value = []
  activeCategoryId.value = ''
  contentScrollContainer.value = undefined
  visible.value = true
  loadStoreTools()
}

/* 锚点 */
const contentScrollContainer = shallowRef<HTMLElement>()
const storeLayoutRef = useTemplateRef<{ getScrollContainer: () => HTMLElement | undefined; setScrollTop: (scrollTop: number) => void }>('storeLayoutRef')

function handleCategoryAnchorChange(href: string) {
  activeCategoryId.value = href.slice(TOOL_STORE_CATEGORY_ANCHOR_PREFIX.length)
}

function handleCategoryAnchorClick(event: MouseEvent) {
  event.preventDefault()
}

function handleAddSuccess() {
  visible.value = false
  emit('refresh')
}

function handleClosed() {
  storeToolsLoadSequence++
  loading.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" align-center class="mk-aside-content-dialog" title="工具商店" width="1200" @closed="handleClosed">
    <template #header="{ titleId }">
      <div class="relative flex items-center">
        <h4 :id="titleId">工具商店</h4>
        <MkSearchInput v-model="searchKeyword" class="absolute left-1/2 w-80! -translate-x-1/2" placeholder="搜索" @change="loadStoreTools" />
      </div>
    </template>

    <MkViewLayout ref="storeLayoutRef" :loading="loading" title="">
      <template #aside>
        <el-scrollbar class="min-h-0 flex-1">
          <el-anchor
            v-if="!hasSearchKeyword"
            class="px-4 py-2"
            :container="contentScrollContainer"
            :marker="false"
            :offset="24"
            select-scroll-top
            @change="handleCategoryAnchorChange"
            @click="handleCategoryAnchorClick"
          >
            <el-anchor-link v-for="category in toolStoreCategories" :key="category.id" :href="`${TOOL_STORE_CATEGORY_ANCHOR_PREFIX}${category.id}`">
              <MkListItem :active="activeCategoryId === category.id">
                {{ category.title }}
              </MkListItem>
            </el-anchor-link>
          </el-anchor>
        </el-scrollbar>
      </template>

      <div class="pt-4">
        <!-- 搜索之后的 -->
        <template v-if="hasSearchKeyword && !loading">
          <div class="mb-4 font-semibold">
            找到 <span class="text-primary">{{ storeTools.length }}</span> 个相关工具
          </div>

          <div class="mk-resource-card-grid-sm">
            <template v-for="tool in storeTools" :key="`${tool.source}-${tool.id}`">
              <ToolStoreCard :category-title="categoryTitles[tool.label || 'other'] ?? tool.label ?? '其他'" :folder-id="folderId" :tool="tool" @refresh="handleAddSuccess" />
            </template>
          </div>
          <MkEmpty v-if="!storeTools.length" type="search" />
        </template>
        <!-- 未搜索 -->
        <template v-else-if="storeTools.length">
          <section v-for="category in toolStoreCategories" :id="`tool-store-category-${category.id}`" :key="category.id" class="mb-8 scroll-mt-4">
            <h4 class="mb-4">{{ category.title }}</h4>
            <div class="mk-resource-card-grid-sm">
              <template v-for="tool in category.tools" :key="`${tool.source}-${tool.id}`">
                <ToolStoreCard :category-title="category.title" :folder-id="folderId" :tool="tool" @refresh="handleAddSuccess" />
              </template>
            </div>
          </section>
        </template>
        <MkEmpty v-else-if="!loading" class="mt-24" />
      </div>
    </MkViewLayout>
  </MkDialog>
</template>

<style scoped lang="scss"></style>
