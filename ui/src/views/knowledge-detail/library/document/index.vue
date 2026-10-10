<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { CascaderOption } from 'element-plus'
import type MkQuickCreate from '@/components/global/mk-table/MkQuickCreate.vue'
import MkEditName from '@/components/mk-edit-name/index.vue'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import SharedDocumentApi from '@/api/admin/workspace/shared/knowledge/document'
import KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import SharedKnowledgeApi from '@/api/admin/workspace/shared/knowledge/knowledge'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import { DOCUMENT_TASK_TYPE } from '@/api/enums'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { DOCUMENT_HIT_HANDLING_LABELS } from '@/constants/document'
import { DOCUMENT_STATUS_FILTER_OPTIONS } from './status'
import type { Dict, DocumentHitHandling, DocumentItem, OptionItem } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { isWorkspaceSharedResource } from '@/utils/resource-context'
import { numberFormat } from '@/utils/number'
import { MsgSuccess } from '@/utils/message'
import { getFileIconUrl } from '@/utils/icon'
import ButtonUploadDocument from './upload-document/ButtonUploadDocument.vue'
import ButtonImportDocument from './import-document/ButtonImportDocument.vue'
import { useKnowledgeDetailContext } from '../../context'
import DocumentStatus from './components/DocumentStatus.vue'
import DocumentTags from './components/DocumentTags.vue'
import {
  BatchEmbeddingAction,
  BatchCancelTaskAction,
  DeleteDocumentAction,
  EmbeddingDocumentAction,
  GenerateQuestionsAction,
  BatchGenerateQuestionsAction,
  DownloadDocumentAction,
  ExportDocumentAction,
  BatchExportDocumentAction,
  MigrateDocumentAction,
  ReplaceDocumentAction,
  SettingDocumentAction,
  BatchSettingDocumentAction,
  SyncDocumentAction,
  BatchSyncDocumentAction,
  TokenizeDocumentAction,
  BatchTokenizeAction,
} from './action-dropdown'

defineOptions({ name: 'DocumentListView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const route = useRoute()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))
const knowledgeType = computed(() => String(route.params.type ?? ''))
const { knowledge } = useKnowledgeDetailContext()

/* 快速创建 */
const showQuickCreate = computed(() => knowledgeType.value === KNOWLEDGE_TYPE_KEY.BASE && !isWorkspaceSharedResource())
const quickCreateRef = ref<InstanceType<typeof MkQuickCreate>>()

function handleCreateDocument(name: string) {
  loading.value = true
  return DocumentApi.putBatchCreateDocuments(knowledgeId.value, [{ name }])
    .then(() => {
      // 创建成功即清理草稿，后续刷新失败不恢复为可重复提交的输入。
      quickCreateRef.value?.close()
      MsgSuccess('创建成功')
      paginationConfig.value.currentPage = 1
      return loadDocuments()
    })
    .catch(() => {
      // 请求层统一提示错误，创建失败时保留输入。
    })
    .finally(() => {
      loading.value = false
    })
}

/* 文档名称编辑 */
function validateDocumentName(name: string): string | undefined {
  if (/[:\\/?*\[\]]/.test(name)) {
    return '文件名称不能包含以下特殊字符：: \\ / ? * [ ]'
  }
}

function saveDocumentName(documentId: string, name: string): Promise<string> {
  return DocumentApi.putDocument(knowledgeId.value, documentId, { name }).then((document) => {
    // 轮询可能已替换行对象，按 ID 更新当前列表中的名称与更新时间。
    const currentDocument = documentData.value.find(({ id }) => id === documentId)
    if (currentDocument) {
      currentDocument.name = document.name
      currentDocument.update_time = document.update_time
    }
    return document.name
  })
}

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
const selectedDocumentStatus = ref<string | null>(null)
const documentStatusFilter = computed(() => DOCUMENT_STATUS_FILTER_OPTIONS.find(({ value }) => value === selectedDocumentStatus.value))

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
  clearDocumentSelection()
  paginationConfig.value.currentPage = 1
  return loadDocuments()
}

/* 文档列表轮询：后台刷新保留筛选、分页和选择。 */
let pollingTimer: ReturnType<typeof setTimeout> | undefined
let pollingActive = false

function stopPolling() {
  clearTimeout(pollingTimer)
  pollingTimer = undefined
}

function schedulePolling() {
  stopPolling()
  if (!pollingActive) return
  pollingTimer = setTimeout(() => {
    if (loading.value || operationLoading.value) {
      schedulePolling()
      return
    }
    void loadDocuments(false).catch(() => {
      // 请求层统一提示错误，失败后仍由 finally 安排下一次轮询。
    })
  }, 6000)
}

function loadDocuments(showLoading = true): Promise<void> {
  stopPolling()
  if (showLoading) loading.value = true
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
      if (!pollingActive) return
      documentData.value = page.records
      paginationConfig.value.total = page.total
      // 删除或迁移最后一页文档后，回到仍有数据的最后一页。
      const lastPage = Math.max(1, Math.ceil(page.total / paginationConfig.value.pageSize))
      if (paginationConfig.value.currentPage > lastPage) {
        paginationConfig.value.currentPage = lastPage
        return loadDocuments(showLoading)
      }
    })
    .finally(() => {
      if (showLoading) loading.value = false
      schedulePolling()
    })
}

function handleSearchChange(query?: Dict<unknown>) {
  clearDocumentSelection()
  documentQuery.value = query ?? {}
  paginationConfig.value.currentPage = 1
  return loadDocuments()
}

/* 导入成功后清空查询条件，重新加载第一页。 */
function handleImportDocumentSuccess() {
  selectedDocumentStatus.value = null
  selectedDocumentActive.value = null
  selectedDocumentHitHandling.value = null
  selectedDocumentTags.value = []
  return handleSearchChange()
}

/* 批量操作 */
const documentTableRef = ref<{ clearSelection: () => void }>()
const selectedDocuments = ref<DocumentItem[]>([])
const selectedDocumentIds = computed(() => selectedDocuments.value.map(({ id }) => id))

function handleSelectionChange(documents: unknown[]) {
  selectedDocuments.value = documents as DocumentItem[]
}

function clearDocumentSelection() {
  documentTableRef.value?.clearSelection()
  selectedDocuments.value = []
}

/* 单项与批量文档操作 */
// 共用操作状态，防止重复提交。
const operationLoading = ref(false)

// 文档启停由服务端结果与列表刷新回显，避免开关提前修改状态。
function handleChangeActive(document: DocumentItem) {
  if (operationLoading.value) return false
  operationLoading.value = true
  return DocumentApi.putDocument(knowledgeId.value, document.id, { is_active: !document.is_active })
    .then(() => {
      MsgSuccess('操作成功')
      return refreshAfterOperation().then(() => false)
    })
    .catch(() => false)
    .finally(() => {
      operationLoading.value = false
    })
}

// 操作成功后清空勾选并刷新文档列表。
function refreshAfterOperation() {
  // 清空勾选会卸载批量 Action，先释放操作状态，避免其 finally 无法回写 loading。
  operationLoading.value = false
  clearDocumentSelection()
  return loadDocuments()
}

onMounted(() => {
  pollingActive = true
  loadDocuments()
})

onBeforeUnmount(() => {
  pollingActive = false
  stopPolling()
})
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between w-full gap-4">
      <h4>{{ title }}</h4>
      <div class="flex-align-center gap-3">
        <MkComplexSearch :fields="searchFields" @change="handleSearchChange" />
        <!-- 导入 Web、飞书或工作流文档 -->
        <ButtonImportDocument
          v-if="!showQuickCreate && !isWorkspaceSharedResource()"
          :api="DocumentApi"
          :knowledge-id="knowledgeId"
          :knowledge-type="knowledgeType"
          :folder-token="String(knowledge?.meta?.folder_token ?? '')"
          :workflow="knowledge?.work_flow"
          @refresh="handleImportDocumentSuccess"
        />
        <!-- 上传文档 -->
        <ButtonUploadDocument
          v-if="showQuickCreate"
          :api="DocumentApi"
          :knowledge-id="knowledgeId"
          :file-count-limit="knowledge?.file_count_limit"
          :file-size-limit="knowledge?.file_size_limit"
          @refresh="handleImportDocumentSuccess"
        />
      </div>
    </div>
  </Teleport>
  <MkTable
    ref="documentTableRef"
    v-loading="loading || operationLoading"
    :data="documentData"
    v-model:pagination-config="paginationConfig"
    :max-table-height="210"
    @current-change="loadDocuments()"
    @size-change="loadDocuments()"
    @selection-change="handleSelectionChange"
    resizable
  >
    <template v-if="showQuickCreate" #body-prepend>
      <!-- 快速创建空白文档 -->
      <MkQuickCreate ref="quickCreateRef" text="快速创建空白文档" placeholder="请输入文档名称" @create="handleCreateDocument" />
    </template>

    <el-table-column v-if="!isWorkspaceSharedResource()" type="selection" width="40" reserve-selection />

    <el-table-column prop="name" label="文档名称" min-width="220" show-overflow-tooltip>
      <template #default="{ row }: { row: DocumentItem }">
        <!-- 编辑文档名称 -->
        <MkEditName
          :key="row.id"
          v-model="row.name"
          :disabled="isWorkspaceSharedResource()"
          :maxlength="128"
          :validate="validateDocumentName"
          :save="(name) => saveDocumentName(row.id, name)"
        >
          <template #prefix>
            <img v-if="knowledgeType === KNOWLEDGE_TYPE_KEY.WEB" src="@/assets/file-type/web-link-icon.svg" alt="" class="size-5" />
            <img v-else :src="getFileIconUrl(row.name)" alt="" class="size-5" />
          </template>
        </MkEditName>
      </template>
    </el-table-column>

    <el-table-column width="140">
      <template #header>
        <MkTableFilter
          v-model="selectedDocumentStatus"
          mode="single"
          label="文件状态"
          :options="DOCUMENT_STATUS_FILTER_OPTIONS"
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
    <el-table-column v-if="!isWorkspaceSharedResource()" label="操作" width="160" fixed="right">
      <template #default="{ row }: { row: DocumentItem }">
        <div class="flex-align-center" @click.stop>
          <!-- 启用或禁用文档 -->
          <el-switch :model-value="row.is_active" size="small" :disabled="operationLoading" :before-change="() => handleChangeActive(row)" />

          <el-divider direction="vertical" class="ml-3! mr-2!" />

          <div class="flex">
            <!-- 向量化或取消向量化 -->
            <EmbeddingDocumentAction
              :api="DocumentApi"
              :knowledge-id="knowledgeId"
              :document="row"
              v-model:loading="operationLoading"
              @refresh="refreshAfterOperation"
            />
            <!-- 分词索引或取消分词索引 -->
            <TokenizeDocumentAction
              :api="DocumentApi"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document="row"
              @refresh="refreshAfterOperation"
            />
            <!-- 更多文档操作 -->
            <MkTableMoreDropdown>
              <!-- 生成或取消生成问题 -->
              <GenerateQuestionsAction
                :api="DocumentApi"
                v-model:loading="operationLoading"
                :knowledge-id="knowledgeId"
                :document="row"
                @refresh="refreshAfterOperation"
              />
              <!-- 设置文档标签 -->
              <!-- <DocumentTagsAction
                :api="DocumentApi"
                :knowledge-id="knowledgeId"
                :document-ids="[row.id]"
                manage-tags
                :disabled="operationLoading"
                @refresh="refreshAfterOperation"
              /> -->
              <!-- 同步 -->
              <SyncDocumentAction
                v-if="knowledgeType === KNOWLEDGE_TYPE_KEY.WEB || knowledgeType === KNOWLEDGE_TYPE_KEY.LARK || (knowledgeType === KNOWLEDGE_TYPE_KEY.WORKFLOW && row.meta?.source_type === 'web')"
                label="同步"
                :api="DocumentApi"
                :knowledge-id="knowledgeId"
                :document="row"
                v-model:loading="operationLoading"
                @refresh="refreshAfterOperation"
              />

              <!-- 文档设置 -->
              <SettingDocumentAction
                label="设置"
                icon="icon_setting"
                :api="DocumentApi"
                :knowledge-id="knowledgeId"
                :document="row"
                v-model:loading="operationLoading"
                @refresh="refreshAfterOperation"
              />

              <!-- 迁移文档 -->
              <MigrateDocumentAction
                label="迁移"
                icon="icon_move2_outlined"
                :api="DocumentApi"
                :knowledge-id="knowledgeId"
                :document-ids="[row.id]"
                :disabled="operationLoading"
                @refresh="refreshAfterOperation"
              />
              <!-- 导出文档 -->
              <ExportDocumentAction label="导出" :api="DocumentApi" v-model:loading="operationLoading" :document="row" />

              <template v-if="knowledgeType === KNOWLEDGE_TYPE_KEY.BASE || knowledgeType === KNOWLEDGE_TYPE_KEY.WORKFLOW">
                <!-- 下载原文档 -->
                <DownloadDocumentAction :api="DocumentApi" :knowledge-id="knowledgeId" v-model:loading="operationLoading" :document="row" />
                <!-- 替换原文档 -->
                <ReplaceDocumentAction
                  :api="DocumentApi"
                  :knowledge-id="knowledgeId"
                  v-model:loading="operationLoading"
                  :document="row"
                  @refresh="refreshAfterOperation"
                />
              </template>
              <!-- 删除文档 -->
              <DeleteDocumentAction
                divided
                icon="icon_delete-trash_outlined"
                :api="DocumentApi"
                :knowledge-id="knowledgeId"
                v-model:loading="operationLoading"
                :document="row"
                @refresh="refreshAfterOperation"
              />
            </MkTableMoreDropdown>
          </div>
        </div>
      </template>
    </el-table-column>
    <template v-if="!isWorkspaceSharedResource()" #footer-batch-actions>
      <!-- 批量向量化 -->
      <BatchEmbeddingAction
        :api="DocumentApi"
        :knowledge-id="knowledgeId"
        :document-ids="selectedDocumentIds"
        v-model:loading="operationLoading"
        @refresh="refreshAfterOperation"
      />
      <!-- 批量分词索引 -->
      <BatchTokenizeAction
        :api="DocumentApi"
        :knowledge-id="knowledgeId"
        v-model:loading="operationLoading"
        :document-ids="selectedDocumentIds"
        @refresh="refreshAfterOperation"
      />
      <!-- 批量生成问题 -->
      <BatchGenerateQuestionsAction
        :api="DocumentApi"
        v-model:loading="operationLoading"
        :knowledge-id="knowledgeId"
        :document-ids="selectedDocumentIds"
        :disabled="operationLoading"
        @refresh="refreshAfterOperation"
      />
      <!-- 批量文档设置 -->
      <BatchSettingDocumentAction
        label="设置"
        :api="DocumentApi"
        :knowledge-id="knowledgeId"
        :document-ids="selectedDocumentIds"
        v-model:loading="operationLoading"
        @refresh="refreshAfterOperation"
      />

      <!-- 批量添加标签 -->
      <!-- <el-button>添加标签</el-button> -->

      <!-- 更多批量操作 -->
      <MkDropdown class="ml-3" trigger="click" placement="bottom-end" hide-when-empty persistent>
        <!-- 展开更多批量操作 -->
        <el-button plain type="primary" class="min-w-0! w-8!">
          <MkIcon name="icon_more_outlined" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu>
            <!-- 批量同步 -->
            <BatchSyncDocumentAction
              v-if="knowledgeType === KNOWLEDGE_TYPE_KEY.WEB || knowledgeType === KNOWLEDGE_TYPE_KEY.LARK"
              label="同步"
              :api="DocumentApi"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document-ids="selectedDocumentIds"
              @refresh="refreshAfterOperation"
            />
            <!-- 批量迁移文档 -->
            <MigrateDocumentAction
              label="迁移"
              :api="DocumentApi"
              :knowledge-id="knowledgeId"
              :document-ids="selectedDocumentIds"
              :disabled="operationLoading"
              @refresh="refreshAfterOperation"
            />

            <!-- 批量导出文档 -->
            <BatchExportDocumentAction label="导出" :api="DocumentApi" v-model:loading="operationLoading" :document-ids="selectedDocumentIds" />
            <!-- 批量取消向量化 -->
            <BatchCancelTaskAction
              :api="DocumentApi"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document-ids="selectedDocumentIds"
              :task-type="DOCUMENT_TASK_TYPE.EMBEDDING"
              label="取消向量化"
              divided
              @refresh="refreshAfterOperation"
            />
            <!-- 批量取消生成问题 -->
            <BatchCancelTaskAction
              :api="DocumentApi"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document-ids="selectedDocumentIds"
              :task-type="DOCUMENT_TASK_TYPE.GENERATE_PROBLEM"
              label="取消生成"
              @refresh="refreshAfterOperation"
            />
            <!-- 批量删除文档 -->
            <DeleteDocumentAction
              :api="DocumentApi"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document-ids="selectedDocumentIds"
              batch
              @refresh="refreshAfterOperation"
            />
          </MkDropdownMenu>
        </template>
      </MkDropdown>
    </template>
  </MkTable>
</template>
