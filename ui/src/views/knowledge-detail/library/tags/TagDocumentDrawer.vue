<script setup lang="ts">
import { computed, ref } from 'vue'
import { cloneDeep } from 'lodash'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { Dict, DocumentItem, KnowledgeTagUpdatePayload } from '@/api/types'
import { getFileIconUrl } from '@/utils/icon'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'TagDocumentDrawer' })

const props = defineProps<{ knowledgeId: string; api: typeof DocumentApi }>()
const emit = defineEmits<{ refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const currentTag = ref<KnowledgeTagUpdatePayload>()
const title = computed(() => (currentTag.value ? `${currentTag.value.key}—${currentTag.value.value}` : '关联文档'))
const activeTab = ref<'linked' | 'unlinked'>('linked')
const searchName = ref('')
const documentActiveOptions = [
  { label: '已启用', value: true },
  { label: '已禁用', value: false },
]
const selectedDocumentActive = ref<boolean | null>(null)
const documentData = ref<DocumentItem[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 10, total: 0 })
const documentTableRef = ref<{ clearSelection: () => void }>()
const selectedDocuments = ref<DocumentItem[]>([])
const selectedDocumentIds = computed(() => new Set(selectedDocuments.value.map(({ id }) => id)))

/* 两个页签复用同一文档查询，未关联页通过 tag_exclude 排除当前标签。 */
function loadDocuments(): Promise<void> {
  if (!currentTag.value) return Promise.resolve()
  clearSelection()
  loading.value = true
  const query: Dict<unknown> = {
    resource_type: 'document',
    tags: [currentTag.value.id],
    is_active: selectedDocumentActive.value ?? undefined,
    ...(activeTab.value === 'unlinked' ? { tag_exclude: true } : {}),
    ...(searchName.value.trim() ? { name: searchName.value.trim() } : {}),
  }
  return props.api
    .getDocumentPage(props.knowledgeId, paginationConfig.value, query)
    .then((page) => {
      const lastPage = Math.max(1, Math.ceil(page.total / paginationConfig.value.pageSize))
      if (paginationConfig.value.currentPage > lastPage) {
        paginationConfig.value.currentPage = lastPage
        return loadDocuments()
      }
      documentData.value = page.records
      paginationConfig.value.total = page.total
    })
    .catch((error) => {
      // 查询失败后不保留上一页签的数据，避免按新的关联方向操作旧记录。
      documentData.value = []
      paginationConfig.value.total = 0
      throw error
    })
    .finally(() => {
      loading.value = false
    })
}

function open(tag: KnowledgeTagUpdatePayload) {
  currentTag.value = cloneDeep(tag)
  visible.value = true
  return loadDocuments()
}

function clearSelection() {
  documentTableRef.value?.clearSelection()
  selectedDocuments.value = []
}

function handleSelectionChange(selection: unknown[]) {
  selectedDocuments.value = selection as DocumentItem[]
}

function getRowClass({ row }: { row: DocumentItem }) {
  return selectedDocumentIds.value.has(row.id) ? '[&>td]:bg-primary/10!' : ''
}

function handleDocumentFilterChange() {
  if (loading.value) return
  paginationConfig.value.currentPage = 1
  return loadDocuments()
}

function handleComplexSearchChange(query?: Dict<unknown>) {
  searchName.value = typeof query?.name === 'string' ? query.name : ''
  return handleDocumentFilterChange()
}

function handleTabChange() {
  searchName.value = ''
  selectedDocumentActive.value = null
  paginationConfig.value.currentPage = 1
  return loadDocuments()
}

/* 单个和批量操作共用现有文档标签关联协议。 */
function handleLinkDocuments(documentIds: string[]) {
  if (loading.value || !currentTag.value || !documentIds.length) return
  const unlink = activeTab.value === 'linked'
  loading.value = true
  const request = unlink
    ? props.api.putUnlinkTagDocuments(props.knowledgeId, currentTag.value.id, documentIds)
    : props.api.postAddDocumentTags(props.knowledgeId, documentIds, [currentTag.value.id])
  return request
    .then(() => {
      MsgSuccess(unlink ? '取消关联成功' : '关联成功')
      emit('refresh')
      return loadDocuments()
    })
    .finally(() => {
      loading.value = false
    })
}

function handleBatchLinkDocuments() {
  return handleLinkDocuments(selectedDocuments.value.map(({ id }) => id))
}

function handleBeforeClose(done: () => void) {
  if (!loading.value) done()
}

function resetData() {
  currentTag.value = undefined
  activeTab.value = 'linked'
  searchName.value = ''
  selectedDocumentActive.value = null
  documentData.value = []
  paginationConfig.value = { currentPage: 1, pageSize: 10, total: 0 }
  clearSelection()
  loading.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="title" :before-close="handleBeforeClose" size="840" @closed="resetData">
    <div class="flex-column gap-4" :inert="loading">
      <el-tabs v-model="activeTab" :before-leave="() => !loading" @tab-change="handleTabChange">
        <el-tab-pane label="已关联文档" name="linked" />
        <el-tab-pane label="未关联文档" name="unlinked" />
      </el-tabs>
      <div class="flex-between gap-3">
        <!-- 批量关联或取消关联文档 -->
        <el-button plain :disabled="!selectedDocuments.length || loading" @click="handleBatchLinkDocuments">
          <MkIcon :name="activeTab === 'linked' ? 'icon_unlink_outlined' : 'icon_link-record_outlined'" />
          <span>{{ activeTab === 'linked' ? '取消关联' : '关联' }}</span>
        </el-button>
        <MkSearchInput v-if="activeTab === 'linked'" v-model="searchName" class="w-60!" @change="handleDocumentFilterChange" />
        <MkComplexSearch v-else :fields="[{ label: '名称', value: 'name' }]" @change="handleComplexSearchChange" />
      </div>
      <!-- 仅遮罩表格，指示器固定在表体靠上位置，避免随记录数量上下跳动。 -->
      <div v-loading="loading" element-loading-custom-class="[&>.el-loading-spinner]:top-20!" class="relative">
        <MkTable
          ref="documentTableRef"
          v-model:pagination-config="paginationConfig"
          :data="documentData"
          :row-class-name="getRowClass"
          row-key="id"
          @current-change="loadDocuments"
          @size-change="loadDocuments"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="40" />
          <el-table-column prop="name" label="文档名称" min-width="200">
            <template #default="{ row }: { row: DocumentItem }">
              <div class="flex-align-center gap-2">
                <img :src="getFileIconUrl(row.name)" alt="" class="size-5 shrink-0" />
                <span class="truncate" :title="row.name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="启用状态" width="120">
            <template #header>
              <MkTableFilter
                v-model="selectedDocumentActive"
                mode="single"
                label="启用状态"
                :options="documentActiveOptions"
                @change="handleDocumentFilterChange"
              />
            </template>
            <template #default="{ row }: { row: DocumentItem }">
              <MkStatusLabel :active="row.is_active" />
            </template>
          </el-table-column>
          <el-table-column prop="create_time" label="创建时间" width="180">
            <template #default="{ row }: { row: DocumentItem }">{{ datetimeFormat(row.create_time) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="70" fixed="right">
            <template #default="{ row }: { row: DocumentItem }">
              <!-- 关联或取消关联当前文档 -->
              <MkAction
                display="button"
                :label="activeTab === 'linked' ? '取消关联' : '关联'"
                :icon="activeTab === 'linked' ? 'icon_unlink_outlined' : 'icon_link-record_outlined'"
                :disabled="loading"
                @click="handleLinkDocuments([row.id])"
              />
            </template>
          </el-table-column>
        </MkTable>
      </div>
    </div>
  </MkDrawer>
</template>
