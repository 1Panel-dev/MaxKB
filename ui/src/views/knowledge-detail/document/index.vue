<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { CascaderOption } from 'element-plus'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import SharedDocumentApi from '@/api/admin/workspace/shared/knowledge/document'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedKnowledgeApi from '@/api/admin/workspace/shared/knowledge/knowledge'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import { DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE, STATE_TYPES } from '@/api/enums'
import { DOCUMENT_HIT_HANDLING_LABELS } from '@/constants/document'
import { STATE_LABELS } from '@/constants/state'
import type { Dict, DocumentHitHandling, DocumentItem, OptionItem } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { isWorkspaceSharedResource } from '@/utils/resource-context'
import { numberFormat } from '@/utils/number'
import DocumentStatus from './components/DocumentStatus.vue'
import DocumentTags from './components/DocumentTags.vue'

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

/* 过滤项 */
// 文档状态
interface DocumentStatusFilter {
  label: string
  value: string
  status: (typeof DOCUMENT_TASK_STATE)[keyof typeof DOCUMENT_TASK_STATE]
  task_type?: (typeof DOCUMENT_TASK_TYPE)[keyof typeof DOCUMENT_TASK_TYPE]
}
const documentStatusOptions: DocumentStatusFilter[] = [
  { label: STATE_LABELS[STATE_TYPES.SUCCESS], value: STATE_TYPES.SUCCESS, status: DOCUMENT_TASK_STATE.SUCCESS },
  { label: STATE_LABELS[STATE_TYPES.FAILURE], value: STATE_TYPES.FAILURE, status: DOCUMENT_TASK_STATE.FAILURE },
  {
    label: STATE_LABELS[STATE_TYPES.EMBEDDING],
    value: STATE_TYPES.EMBEDDING,
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.EMBEDDING,
  },
  {
    label: STATE_LABELS[STATE_TYPES.TOKENIZE],
    value: STATE_TYPES.TOKENIZE,
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.TOKENIZE,
  },
  { label: STATE_LABELS[STATE_TYPES.PENDING], value: STATE_TYPES.PENDING, status: DOCUMENT_TASK_STATE.PENDING },
  {
    label: STATE_LABELS[STATE_TYPES.GENERATE],
    value: STATE_TYPES.GENERATE,
    status: DOCUMENT_TASK_STATE.STARTED,
    task_type: DOCUMENT_TASK_TYPE.GENERATE_PROBLEM,
  },
]
const selectedDocumentStatus = ref<string | null>(null)
const documentStatusFilter = computed(() => documentStatusOptions.find(({ value }) => value === selectedDocumentStatus.value))

// 启用状态
const documentActiveOptions = [
  { label: '已启用', value: true },
  { label: '已禁用', value: false },
]
const selectedDocumentActive = ref<boolean | null>(null)

// 召回处理
const documentHitHandlingOptions = Object.entries(DOCUMENT_HIT_HANDLING_LABELS).map(([value, label]) => ({ value, label }))
const selectedDocumentHitHandling = ref<DocumentHitHandling | null>(null)

// 标签
const selectedDocumentTags = ref<string[]>([])
const documentTagOptions = ref<CascaderOption[]>([])
const documentTagLoading = ref(false)

function loadDocumentTagOptions() {
  // 加载成功后至少有“无标签”选项，无需额外维护 loaded 状态。
  if (documentTagLoading.value || documentTagOptions.value.length) return
  documentTagLoading.value = true
  const requestApi = isWorkspaceSharedResource() ? SharedKnowledgeApi : KnowledgeApi
  return requestApi
    .getKnowledgeTags(knowledgeId.value)
    .then((groups) => {
      documentTagOptions.value = [
        ...groups.map((group) => ({
          label: group.key,
          value: `key:${group.key}`,
          children: group.values.map((tag) => ({ label: tag.value, value: tag.id })),
        })),
        { label: '无标签', value: 'NO_TAG' },
      ]
    })
    .finally(() => {
      documentTagLoading.value = false
    })
}

function handleDocumentFilterChange() {
  paginationConfig.value.currentPage = 1
  return loadDocuments()
}

function loadDocuments() {
  loading.value = true
  const requestApi = isWorkspaceSharedResource() ? SharedDocumentApi : DocumentApi
  return requestApi
    .getDocumentPage(knowledgeId.value, paginationConfig.value, {
      ...documentQuery.value,
      status: documentStatusFilter.value?.status,
      task_type: documentStatusFilter.value?.task_type,
      is_active: selectedDocumentActive.value ?? undefined,
      hit_handling_method: selectedDocumentHitHandling.value ?? undefined,
      tags: selectedDocumentTags.value.length ? selectedDocumentTags.value : undefined,
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
  loadDocuments()
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
    resizable
  >
    <!-- <template #append>快速添加</template> -->
    <el-table-column prop="name" label="文档名称" min-width="220" show-overflow-tooltip />

    <el-table-column width="140">
      <template #header>
        <MkTableFilter
          v-model="selectedDocumentStatus"
          mode="single"
          label="文件状态"
          :options="documentStatusOptions"
          @change="handleDocumentFilterChange"
        />
      </template>
      <template #default="{ row }: { row: DocumentItem }">
        <DocumentStatus :status="row.status" :status-meta="row.status_meta" />
      </template>
    </el-table-column>
    <el-table-column width="120">
      <template #header>
        <MkTableFilter
          v-model="selectedDocumentActive"
          mode="single"
          label="启用状态"
          :options="documentActiveOptions"
          @change="handleDocumentFilterChange"
        />
      </template>
      <template #default="{ row }"><MkStatusLabel :active="row.is_active" /></template>
    </el-table-column>
    <el-table-column prop="char_length" label="字符数">
      <template #default="{ row }">
        {{ numberFormat(row.char_length) }}
      </template>
    </el-table-column>
    <el-table-column prop="paragraph_count" label="分段">
      <template #default="{ row }">
        {{ numberFormat(row.paragraph_count) }}
      </template>
    </el-table-column>
    <!-- 标签 -->
    <el-table-column min-width="150">
      <template #header>
        <MkTableFilter
          v-model="selectedDocumentTags"
          mode="cascader"
          label="标签"
          :options="documentTagOptions"
          @open="loadDocumentTagOptions"
          @change="handleDocumentFilterChange"
        />
      </template>
      <template #default="{ row }: { row: DocumentItem }">
        <DocumentTags :document="row" />
      </template>
    </el-table-column>

    <el-table-column width="130">
      <template #header>
        <MkTableFilter
          v-model="selectedDocumentHitHandling"
          mode="single"
          label="召回处理"
          :options="documentHitHandlingOptions"
          @change="handleDocumentFilterChange"
        />
      </template>
      <template #default="{ row }: { row: DocumentItem }">
        {{ DOCUMENT_HIT_HANDLING_LABELS[row.hit_handling_method] }}
      </template>
    </el-table-column>
    <el-table-column prop="hit_num" label="召回次数">
      <template #default="{ row }">
        {{ numberFormat(row.hit_num) }}
      </template>
    </el-table-column>
    <el-table-column label="最后一次召回时间" width="180">
      <template #default="{ row }">{{ datetimeFormat(row.last_hit_time) }}</template>
    </el-table-column>
    <el-table-column prop="nick_name" label="创建者" show-overflow-tooltip />
    <el-table-column label="更新时间" width="180">
      <template #default="{ row }">{{ datetimeFormat(row.update_time) }}</template>
    </el-table-column>
    <el-table-column label="创建时间" width="180">
      <template #default="{ row }">{{ datetimeFormat(row.create_time) }}</template>
    </el-table-column>
  </MkTable>
</template>
