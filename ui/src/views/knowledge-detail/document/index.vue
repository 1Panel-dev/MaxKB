<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import SharedDocumentApi from '@/api/admin/workspace/shared/knowledge/document'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import { DOCUMENT_HIT_HANDLING, DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { Dict, DocumentItem, OptionItem } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { isWorkspaceSharedResource } from '@/utils/resource-context'

defineOptions({ name: 'DocumentListView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const route = useRoute()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))

/* 文档筛选与分页查询 */
const loading = ref(false)
const documentData = ref<DocumentItem[]>([])
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const documentQuery = ref<Dict<unknown>>({})
const creatorOptions = ref<OptionItem<string>[]>([])
const searchFields = computed(() => [
  { label: '名称', value: 'name' },
  { label: '创建者', value: 'create_user', options: creatorOptions.value, remoteMethod: loadCreatorOptions },
])

function loadCreatorOptions(keyword: string) {
  const requestCommonApi = isWorkspaceSharedResource() ? CommonSystemApi : CommonApi
  return requestCommonApi.getAllUsers(keyword ? { nick_name: keyword } : undefined).then((users) => {
    creatorOptions.value = users.map(({ id, nick_name }) => ({ label: nick_name, value: id }))
  })
}

// 过滤项
interface DocumentStatusFilter {
  label: string
  status?: (typeof DOCUMENT_TASK_STATE)[keyof typeof DOCUMENT_TASK_STATE]
  task_type?: (typeof DOCUMENT_TASK_TYPE)[keyof typeof DOCUMENT_TASK_TYPE]
}
const allStatusFilter: DocumentStatusFilter = { label: '全部' }

const documentStatusFilter = ref<DocumentStatusFilter>(allStatusFilter)

function loadDocuments() {
  loading.value = true
  const requestApi = isWorkspaceSharedResource() ? SharedDocumentApi : DocumentApi
  return requestApi
    .getDocumentPage(knowledgeId.value, paginationConfig.value, {
      ...documentQuery.value,
      status: documentStatusFilter.value.status,
      task_type: documentStatusFilter.value.task_type,
      resource_type: 'document',
    })
    .then((page) => {
      documentData.value = page.records
      paginationConfig.value.total = page.total
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  documentQuery.value = query ?? {}
  paginationConfig.value.currentPage = 1
  return loadDocuments()
}

onMounted(() => {
  void loadDocuments().catch(() => {})
})
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between w-full gap-4">
      <h4>{{ title }}</h4>
      <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
    </div>
  </Teleport>
  <MkTable
    v-loading="loading"
    :data="documentData"
    v-model:pagination-config="paginationConfig"
    :max-table-height="210"
    @current-change="loadDocuments"
    @size-change="loadDocuments"
  >
    <el-table-column prop="name" label="文档名称" min-width="220" show-overflow-tooltip />

    <el-table-column prop="status" label="文件状态" width="120">
      <template #default="{ row }">
        <StatusValue :status="row.status" :status-meta="row.status_meta"></StatusValue>
      </template>
    </el-table-column>
    <el-table-column prop="char_length" label="字符数" width="110" />
    <el-table-column prop="paragraph_count" label="分段数" width="100" />
    <el-table-column prop="hit_num" label="召回次数" width="120" />
    <el-table-column label="命中处理" width="110">
      <template #default="{ row }">{{ row.hit_handling_method === DOCUMENT_HIT_HANDLING.DIRECTLY_RETURN ? '直接返回' : '模型优化' }}</template>
    </el-table-column>
    <el-table-column label="启用状态" width="100">
      <template #default="{ row }"><MkStatusLabel :active="row.is_active" /></template>
    </el-table-column>
    <el-table-column prop="nick_name" label="创建者" min-width="120" show-overflow-tooltip />
    <el-table-column label="创建时间" width="180">
      <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
    </el-table-column>
  </MkTable>
</template>
