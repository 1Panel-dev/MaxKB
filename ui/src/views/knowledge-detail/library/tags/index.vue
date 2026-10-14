<script setup lang="ts">
import type TagsApi from '@/api/admin/workspace/knowledge/tags'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { computed, watch, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { TableColumnCtx } from 'element-plus'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { useKnowledgeLibraryContext } from '../../context'
import type { KnowledgeTagGroup, KnowledgeTagUpdatePayload } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import CreateTagDialog from './components/CreateTagDialog.vue'
import EditTagDialog from './components/EditTagDialog.vue'
import ButtonImportTags from './components/ButtonImportTags.vue'
import TagDocumentDrawer from './AssociatedDocumentDrawer.vue'

type WorkspaceDocumentApi = typeof DocumentApi

type WorkspaceTagsApi = typeof TagsApi

defineOptions({ name: 'TagManagementView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

interface TagTableRow extends KnowledgeTagUpdatePayload {
  doc_count?: number
  rowspan: number
}

const { resourceApi, resourceScope } = useKnowledgeLibraryContext()
const route = useRoute()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))
const loading = ref(false)
const operationLoading = ref(false)
const tagGroups = ref<KnowledgeTagGroup[]>([])
const searchText = ref('')
const tagPage = ref({ currentPage: 1, pageSize: 10 })
const tagTableRef = ref<{ clearSelection: () => void }>()
const selectedTags = ref<TagTableRow[]>([])
const hoveredTagKey = ref<string | null>(null)

const paginationConfig = computed({
  get: () => ({ ...tagPage.value, total: tagGroups.value.length }),
  set: ({ currentPage, pageSize }) => {
    tagPage.value = { currentPage, pageSize }
  },
})
const tagRows = computed<TagTableRow[]>(() => {
  const start = (tagPage.value.currentPage - 1) * tagPage.value.pageSize
  return tagGroups.value
    .slice(start, start + tagPage.value.pageSize)
    .flatMap((group) => group.values.map((tag, index) => ({ ...tag, key: group.key, rowspan: index === 0 ? group.values.length : 0 })))
})

function clearSelection() {
  tagTableRef.value?.clearSelection()
  selectedTags.value = []
  hoveredTagKey.value = null
}

function loadTags() {
  clearSelection()
  const requestApi = resourceApi.tags
  if (!requestApi) return Promise.resolve()
  loading.value = true
  const keyword = searchText.value.trim()
  const tagsRequest =
    resourceScope.value === 'workspace' && 'postKnowledgeTags' in requestApi
      ? requestApi.getKnowledgeTags(knowledgeId.value, { name: keyword || undefined })
      : requestApi.getKnowledgeTags(knowledgeId.value)
  return tagsRequest
    .then((groups) => {
      tagGroups.value = keyword ? groups.filter((group) => group.key.includes(keyword)) : groups
      const lastPage = Math.max(1, Math.ceil(tagGroups.value.length / tagPage.value.pageSize))
      tagPage.value.currentPage = Math.min(tagPage.value.currentPage, lastPage)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange() {
  tagPage.value.currentPage = 1
  return loadTags()
}

function handleSelectionChange(selection: unknown[]) {
  selectedTags.value = selection as TagTableRow[]
}

// 这里只合并展示单元格，同组选择由 MkTable 的 selectionGroupKey 处理。
function spanMethod({ column, row }: { column: TableColumnCtx<TagTableRow>; row: TagTableRow }) {
  if (column.type === 'selection' || column.property === 'key') return row.rowspan ? [row.rowspan, 1] : [0, 0]
}

function handleCellEnter(row: TagTableRow) {
  hoveredTagKey.value = row.key
}

function handleCellLeave() {
  hoveredTagKey.value = null
}

/* 共用创建、编辑弹窗和关联文档抽屉。 */
const createTagRef = ref<InstanceType<typeof CreateTagDialog>>()
const editTagRef = ref<InstanceType<typeof EditTagDialog>>()
const tagDocumentRef = ref<InstanceType<typeof TagDocumentDrawer>>()

function handleOpenCreateTag() {
  createTagRef.value?.open()
}

function handleOpenAddTagValue(row: TagTableRow) {
  createTagRef.value?.open(row.key)
}

function handleOpenEditTag(row: TagTableRow) {
  editTagRef.value?.open(row, 'key')
}

function handleOpenEditTagValue(row: TagTableRow) {
  editTagRef.value?.open(row, 'value')
}

function handleOpenTagDocuments(row: TagTableRow) {
  tagDocumentRef.value?.open({ id: row.id, key: row.key, value: row.value })
}

/* 删除只在确认后提交，标签删除与文档取消关联使用不同接口。 */
function handleDeleteTag(row: TagTableRow, type: 'key' | 'one') {
  const requestApi = resourceApi.tags
  if (resourceScope.value !== 'workspace' || !requestApi || !('deleteKnowledgeTag' in requestApi) || loading.value || operationLoading.value) return
  const tagName = type === 'key' ? row.key : `${row.key}—${row.value}`
  return MsgConfirm(`是否删除标签：${tagName}？`, '删除后，使用该标签的资源将会删除该标签，请谨慎操作！').then(
    () => {
      operationLoading.value = true
      return requestApi
        .deleteKnowledgeTag(knowledgeId.value, row.id, type)
        .then(() => {
          MsgSuccess('删除成功')
          return loadTags()
        })
        .finally(() => {
          operationLoading.value = false
        })
    },
    () => {},
  )
}

function handleBatchDelete() {
  const requestApi = resourceApi.tags
  if (
    resourceScope.value !== 'workspace' ||
    !requestApi ||
    !('putBatchDeleteKnowledgeTags' in requestApi) ||
    loading.value ||
    operationLoading.value ||
    !selectedTags.value.length
  )
    return
  const tagIds = selectedTags.value.map(({ id }) => id)
  return MsgConfirm(`是否删除选中的 ${tagIds.length} 个标签？`, '删除后，使用该标签的资源将会删除该标签，请谨慎操作！').then(
    () => {
      operationLoading.value = true
      return requestApi
        .putBatchDeleteKnowledgeTags(knowledgeId.value, tagIds)
        .then(() => {
          MsgSuccess('删除成功')
          return loadTags()
        })
        .finally(() => {
          operationLoading.value = false
        })
    },
    () => {},
  )
}

watch(
  [() => route.params.workspaceId, knowledgeId, resourceScope],
  () => {
    clearSelection()
    tagGroups.value = []
    searchText.value = ''
    tagPage.value = { currentPage: 1, pageSize: 10 }
    void loadTags().catch(() => {})
  },
  { immediate: true },
)
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between gap-4">
      <h4>{{ title }}</h4>
      <div class="flex-align-center">
        <MkSearchInput v-model="searchText" class="mr-3 w-60!" @change="handleSearchChange" />
        <!-- 导入标签，成功后刷新列表 -->
        <ButtonImportTags
          v-if="resourceScope === 'workspace'"
          :api="resourceApi.tags as WorkspaceTagsApi"
          :knowledge-id="knowledgeId"
          :disabled="loading || operationLoading"
          @refresh="loadTags"
        />
        <!-- 创建标签 -->
        <el-button v-if="resourceScope === 'workspace'" type="primary" :disabled="loading || operationLoading" @click="handleOpenCreateTag">
          <MkIcon name="icon_add_outlined" />
          <span>创建</span>
        </el-button>
      </div>
    </div>
  </Teleport>
  <MkTable
    ref="tagTableRef"
    v-model:pagination-config="paginationConfig"
    v-loading="loading || operationLoading"
    :data="tagRows"
    selection-group-key="key"
    :span-method="spanMethod"
    :max-table-height="210"
    @selection-change="handleSelectionChange"
    @current-change="clearSelection"
    @size-change="clearSelection"
    @cell-mouse-enter="handleCellEnter"
    @cell-mouse-leave="handleCellLeave"
  >
    <el-table-column v-if="resourceScope === 'workspace'" type="selection" width="40" />
    <el-table-column prop="key" label="标签" min-width="240">
      <template #default="{ row }: { row: TagTableRow }">
        <div class="flex-align-center gap-1">
          <span class="min-w-0 truncate" :title="row.key">{{ row.key }}</span>
          <div v-if="resourceScope === 'workspace'" class="flex-align-center shrink-0" :class="{ 'group-hover-visible': hoveredTagKey !== row.key }">
            <!-- 添加标签值 -->
            <MkTooltip content="添加标签值" placement="top">
              <el-button type="primary" text @click="handleOpenAddTagValue(row)">
                <MkIcon name="icon_add_outlined" />
              </el-button>
            </MkTooltip>
            <!-- 编辑标签 -->
            <MkTooltip content="编辑标签" placement="top">
              <el-button type="primary" text @click="handleOpenEditTag(row)">
                <MkIcon name="icon_edit_outlined" />
              </el-button>
            </MkTooltip>
            <!-- 删除整个标签 -->
            <MkTooltip content="删除标签" placement="top">
              <el-button type="primary" text @click="handleDeleteTag(row, 'key')">
                <MkIcon name="icon_delete-trash_outlined" />
              </el-button>
            </MkTooltip>
          </div>
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="value" label="标签值" min-width="180" class-name="border-l!" show-overflow-tooltip />
    <el-table-column prop="doc_count" label="已关联文档" min-width="140">
      <template #default="{ row }: { row: TagTableRow }">
        <!-- 查看标签关联文档 -->
        <el-button v-if="resourceScope === 'workspace'" type="primary" link class="mk-link" @click="handleOpenTagDocuments(row)">
          {{ row.doc_count ?? 0 }}
        </el-button>
        <span v-else>{{ row.doc_count ?? 0 }}</span>
      </template>
    </el-table-column>
    <el-table-column v-if="resourceScope === 'workspace'" label="操作" width="100" fixed="right">
      <template #default="{ row }: { row: TagTableRow }">
        <div class="flex-align-center">
          <!-- 编辑标签值 -->
          <MkTooltip content="编辑标签值" placement="top">
            <el-button type="primary" text @click="handleOpenEditTagValue(row)">
              <MkIcon name="icon_edit_outlined" />
            </el-button>
          </MkTooltip>
          <!-- 删除标签值 -->
          <MkTooltip content="删除" placement="top">
            <el-button type="primary" text @click="handleDeleteTag(row, 'one')">
              <MkIcon name="icon_delete-trash_outlined" />
            </el-button>
          </MkTooltip>
        </div>
      </template>
    </el-table-column>
    <template v-if="resourceScope === 'workspace'" #footer-batch-actions>
      <!-- 批量删除标签 -->
      <el-button type="danger" plain :loading="operationLoading" @click="handleBatchDelete">删除</el-button>
    </template>
  </MkTable>
  <CreateTagDialog
    v-if="resourceScope === 'workspace'"
    ref="createTagRef"
    :api="resourceApi.tags as WorkspaceTagsApi"
    :knowledge-id="knowledgeId"
    @refresh="loadTags"
  />
  <EditTagDialog
    v-if="resourceScope === 'workspace'"
    ref="editTagRef"
    :api="resourceApi.tags as WorkspaceTagsApi"
    :knowledge-id="knowledgeId"
    @refresh="loadTags"
  />
  <TagDocumentDrawer
    v-if="resourceScope === 'workspace'"
    ref="tagDocumentRef"
    :api="resourceApi.document as WorkspaceDocumentApi"
    :knowledge-id="knowledgeId"
    @refresh="loadTags"
  />
</template>
