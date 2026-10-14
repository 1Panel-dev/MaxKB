<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import type { TableColumnCtx } from 'element-plus'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { KnowledgeTagGroup } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import AddTagDialog from './AddTagDialog.vue'

defineOptions({ name: 'DocumentTagsDrawer' })
const props = defineProps<{
  knowledgeId: string
  api: typeof DocumentApi
}>()
const operationLoading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: []; closed: [] }>()

interface DocumentTagRow {
  id: string
  key: string
  value: string
  rowspan: number
}

const visible = ref(false)
const loading = ref(false)
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const tagGroups = ref<KnowledgeTagGroup[]>([])
const searchText = ref('')
const selectedTags = ref<DocumentTagRow[]>([])
const tagTableRef = ref<{ clearSelection: () => void }>()
const addTagRef = ref<InstanceType<typeof AddTagDialog>>()
const addTagMounted = ref(false)

// 按接口返回的分组展开，勾选与删除始终按标签值 ID 处理。
const tagRows = computed<DocumentTagRow[]>(() =>
  tagGroups.value.flatMap((group) => group.values.map((tag, index) => ({ ...tag, key: group.key, rowspan: index === 0 ? group.values.length : 0 }))),
)

function clearSelection() {
  tagTableRef.value?.clearSelection()
  selectedTags.value = []
}

function loadTags() {
  clearSelection()
  loading.value = true
  return props.api
    .getDocumentTags(targetKnowledgeId.value, targetDocumentId.value, { name: searchText.value.trim() || undefined })
    .then((groups) => {
      tagGroups.value = groups
    })
    .catch(() => {
      // 查询失败时清除旧数据，避免继续操作已失效的关联。
      tagGroups.value = []
    })
    .finally(() => {
      loading.value = false
    })
}

function open(documentId: string) {
  if (visible.value || operationLoading.value) return
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = documentId
  visible.value = true
  return loadTags()
}

function handleSelectionChange(selection: unknown[]) {
  selectedTags.value = selection as DocumentTagRow[]
}

function spanMethod({ column, row }: { column: TableColumnCtx<DocumentTagRow>; row: DocumentTagRow }) {
  if (column.type === 'selection' || column.property === 'key') return row.rowspan ? [row.rowspan, 1] : [0, 0]
}

function handleOpenAddTag() {
  addTagMounted.value = true
  return nextTick(() => addTagRef.value?.open([targetDocumentId.value]))
}

function handleTagsChanged() {
  emit('refresh')
  return loadTags()
}

function handleDeleteTags(tags: DocumentTagRow[]) {
  if (loading.value || operationLoading.value || !tags.length) return
  const tagIds = tags.map(({ id }) => id)
  operationLoading.value = true
  return props.api
    .putDeleteDocumentTags(targetKnowledgeId.value, targetDocumentId.value, tagIds)
    .then(() => {
      MsgSuccess('移除成功')
      return handleTagsChanged()
    })
    .finally(() => {
      operationLoading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" title="标签设置" @closed="emit('closed')">
    <div class="flex-between gap-4 mb-4">
      <!-- 为当前文档添加标签 -->
      <el-button type="primary" @click="handleOpenAddTag">
        <MkIcon name="icon_add_outlined" />
        <span>添加标签</span>
      </el-button>
      <MkSearchInput v-model="searchText" class="w-60!" @change="loadTags" />
    </div>
    <MkTable
      ref="tagTableRef"
      v-loading="loading || operationLoading"
      :data="tagRows"
      selection-group-key="key"
      :span-method="spanMethod"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="40" />
      <el-table-column prop="key" label="标签" min-width="160" show-overflow-tooltip />
      <el-table-column prop="value" label="标签值" min-width="160" class-name="border-l!" show-overflow-tooltip />
      <el-table-column label="操作" width="64">
        <template #default="{ row }: { row: DocumentTagRow }">
          <!-- 移除当前文档的标签关联 -->
          <MkTooltip content="删除" placement="top">
            <el-button type="primary" text :disabled="loading || operationLoading" @click="handleDeleteTags([row])">
              <MkIcon name="icon_delete-trash_outlined" />
            </el-button>
          </MkTooltip>
        </template>
      </el-table-column>
      <template #footer-batch-actions>
        <!-- 批量移除当前文档的标签关联 -->
        <el-button plain type="danger" :disabled="loading || operationLoading" @click="handleDeleteTags(selectedTags)">删除</el-button>
      </template>
    </MkTable>
  </MkDrawer>
  <AddTagDialog
    v-if="addTagMounted"
    ref="addTagRef"
    v-model:loading="operationLoading"
    :api="api"
    :knowledge-id="targetKnowledgeId"
    @refresh="handleTagsChanged"
    @closed="addTagMounted = false"
  />
</template>
