<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { TableColumnCtx } from 'element-plus'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import TagsApi from '@/api/admin/workspace/knowledge/tags'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { KnowledgeTagGroup, KnowledgeTagUpdatePayload } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import TagFormDialog from './components/TagFormDialog.vue'
import ButtonImportTags from './components/ButtonImportTags.vue'
import TagDocumentDrawer from './TagDocumentDrawer.vue'

defineOptions({ name: 'TagManagementView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

interface TagTableRow extends KnowledgeTagUpdatePayload {
  doc_count?: number
  rowspan: number
}

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
const selectedTagIds = computed(() => new Set(selectedTags.value.map(({ id }) => id)))

/* 保留完整分组进行搜索和分页，避免同一标签跨页拆开。 */
const filteredTagGroups = computed(() => {
  const keyword = searchText.value.trim().toLocaleLowerCase()
  return tagGroups.value.filter(
    (group) =>
      !keyword || group.key.toLocaleLowerCase().includes(keyword) || group.values.some(({ value }) => value.toLocaleLowerCase().includes(keyword)),
  )
})
const paginationConfig = computed({
  get: () => ({ ...tagPage.value, total: filteredTagGroups.value.length }),
  set: ({ currentPage, pageSize }) => {
    tagPage.value = { currentPage, pageSize }
  },
})
const tagRows = computed<TagTableRow[]>(() => {
  const start = (tagPage.value.currentPage - 1) * tagPage.value.pageSize
  return filteredTagGroups.value
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
  loading.value = true
  return KnowledgeApi.getKnowledgeTags(knowledgeId.value)
    .then((groups) => {
      tagGroups.value = groups
      const lastPage = Math.max(1, Math.ceil(filteredTagGroups.value.length / tagPage.value.pageSize))
      tagPage.value.currentPage = Math.min(tagPage.value.currentPage, lastPage)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange() {
  tagPage.value.currentPage = 1
  clearSelection()
}

function handleSelectionChange(selection: unknown[]) {
  selectedTags.value = selection as TagTableRow[]
}

// 与工作空间成员表格一致：仅合并单元格，不另外联动同组勾选。
function spanMethod({ column, row }: { column: TableColumnCtx<TagTableRow>; row: TagTableRow }) {
  if (column.type === 'selection' || column.property === 'key') return row.rowspan ? [row.rowspan, 1] : [0, 0]
}

function getCellClass({ row }: { row: TagTableRow }) {
  if (selectedTagIds.value.has(row.id)) return 'bg-primary/10!'
  return hoveredTagKey.value === row.key ? 'bg-N100!' : ''
}

function handleCellEnter(row: TagTableRow) {
  hoveredTagKey.value = row.key
}

function handleCellLeave() {
  hoveredTagKey.value = null
}

/* 共用创建、编辑弹窗和关联文档抽屉。 */
const tagFormRef = ref<InstanceType<typeof TagFormDialog>>()
const tagDocumentRef = ref<InstanceType<typeof TagDocumentDrawer>>()

function handleOpenCreateTag() {
  tagFormRef.value?.open()
}

function handleOpenAddTagValue(row: TagTableRow) {
  tagFormRef.value?.open({ mode: 'add-value', key: row.key })
}

function handleOpenEditTag(row: TagTableRow) {
  const group = tagGroups.value.find(({ key }) => key === row.key)
  if (group) tagFormRef.value?.open({ mode: 'edit-group', group })
}

function handleOpenEditTagValue(row: TagTableRow) {
  tagFormRef.value?.open({ mode: 'edit-value', tag: { id: row.id, key: row.key, value: row.value } })
}

function handleOpenTagDocuments(row: TagTableRow) {
  tagDocumentRef.value?.open({ id: row.id, key: row.key, value: row.value })
}

/* 删除只在确认后提交，标签删除与文档取消关联使用不同接口。 */
function handleDeleteTag(row: TagTableRow, type: 'key' | 'one') {
  if (loading.value || operationLoading.value) return
  const tagName = type === 'key' ? row.key : `${row.key}—${row.value}`
  const tip =
    type === 'key'
      ? '删除后，使用该标签的文档将移除此标签及其全部标签值，文档本身不会删除，请谨慎操作！'
      : '删除后，使用该标签值的文档将移除此标签值，文档本身不会删除，请谨慎操作！'
  return MsgConfirm(`是否删除标签：${tagName}？`, tip).then(
    () => {
      operationLoading.value = true
      return TagsApi.deleteKnowledgeTag(knowledgeId.value, row.id, type)
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
  if (loading.value || operationLoading.value || !selectedTags.value.length) return
  const tagIds = selectedTags.value.map(({ id }) => id)
  const groupCount = new Set(selectedTags.value.map(({ key }) => key)).size
  return MsgConfirm(
    `是否删除选中的 ${groupCount} 个标签？`,
    '将删除选中记录所属的标签及其全部标签值，并移除文档上的对应标签；文档本身不会删除，请谨慎操作！',
  ).then(
    () => {
      operationLoading.value = true
      return TagsApi.putBatchDeleteKnowledgeTags(knowledgeId.value, tagIds)
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

onMounted(() => {
  loadTags()
})
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between gap-4">
      <h4>{{ title }}</h4>
      <div class="flex-align-center">
        <MkSearchInput v-model="searchText" class="w-60! mr-3" :disabled="loading || operationLoading" @input="handleSearchChange" />
        <!-- 导入标签，成功后刷新列表 -->
        <ButtonImportTags :api="TagsApi" :knowledge-id="knowledgeId" :disabled="loading || operationLoading" @refresh="loadTags" />
        <!-- 创建标签 -->
        <el-button type="primary" :disabled="loading || operationLoading" @click="handleOpenCreateTag">
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
    :span-method="spanMethod"
    :cell-class-name="getCellClass"
    :max-table-height="210"
    row-key="id"
    row-class-name="group"
    @selection-change="handleSelectionChange"
    @current-change="clearSelection"
    @size-change="clearSelection"
    @cell-mouse-enter="handleCellEnter"
    @cell-mouse-leave="handleCellLeave"
  >
    <el-table-column type="selection" width="40" />
    <el-table-column prop="key" label="标签" min-width="240">
      <template #default="{ row }: { row: TagTableRow }">
        <div class="flex-align-center gap-1">
          <span class="min-w-0 truncate" :title="row.key">{{ row.key }}</span>
          <div class="flex-align-center shrink-0" :class="{ 'group-hover-visible': hoveredTagKey !== row.key }">
            <!-- 新增标签值 -->
            <MkAction display="button" label="新增标签值" icon="icon_add_outlined" @click="handleOpenAddTagValue(row)" />
            <!-- 编辑标签 -->
            <MkAction display="button" label="编辑标签" icon="icon_edit_outlined" @click="handleOpenEditTag(row)" />
            <!-- 删除整个标签 -->
            <MkAction display="button" label="删除标签" icon="icon_delete-trash_outlined" @click="handleDeleteTag(row, 'key')" />
          </div>
        </div>
      </template>
    </el-table-column>
    <el-table-column prop="value" label="标签值" min-width="180" class-name="border-l!" show-overflow-tooltip />
    <el-table-column prop="doc_count" label="已关联文档" min-width="140">
      <template #default="{ row }: { row: TagTableRow }">
        <!-- 查看标签关联文档 -->
        <el-button type="primary" link class="mk-link" @click="handleOpenTagDocuments(row)">{{ row.doc_count ?? 0 }}</el-button>
      </template>
    </el-table-column>
    <el-table-column label="操作" width="100" fixed="right">
      <template #default="{ row }: { row: TagTableRow }">
        <div class="flex-align-center">
          <!-- 编辑标签值 -->
          <MkAction display="button" label="编辑标签值" icon="icon_edit_outlined" @click="handleOpenEditTagValue(row)" />
          <!-- 删除标签值 -->
          <MkAction display="button" label="删除标签值" icon="icon_delete-trash_outlined" @click="handleDeleteTag(row, 'one')" />
        </div>
      </template>
    </el-table-column>
    <template #footer-batch-actions>
      <!-- 批量删除标签 -->
      <el-button type="danger" plain :loading="operationLoading" @click="handleBatchDelete">删除</el-button>
    </template>
  </MkTable>
  <TagFormDialog ref="tagFormRef" :api="TagsApi" :knowledge-id="knowledgeId" @refresh="loadTags" />
  <TagDocumentDrawer ref="tagDocumentRef" :api="DocumentApi" :knowledge-id="knowledgeId" @refresh="loadTags" />
</template>
