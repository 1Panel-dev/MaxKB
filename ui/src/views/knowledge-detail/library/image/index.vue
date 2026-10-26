<script setup lang="ts">
import { perm } from '@/permission'
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { CascaderOption, TableColumnCtx } from 'element-plus'
import MkEditName from '@/components/mk-edit-name/index.vue'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import CommonApi from '@/api/admin/workspace/common'
import CommonSystemApi from '@/api/admin/system/common'
import { DOCUMENT_RESOURCE_TYPE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import { DOCUMENT_HIT_HANDLING_LABELS } from '@/constants/document'
import { DOCUMENT_STATUS_FILTER_OPTIONS } from '../document/status'
import type { Dict, DocumentHitHandling, DocumentItem, OptionItem, ParagraphItem } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { numberFormat } from '@/utils/number'
import { getFileUrl } from '@/utils/common'
import { MsgSuccess } from '@/utils/message'
import { isWorkspaceResource, isWorkspaceSharedResource, isSystemResource } from '@/utils/resource-context'
import ButtonUploadImage from './upload-image/ButtonUploadImage.vue'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import ParagraphDialog from '@/views/document-detail/paragraph-dialog/ParagraphDialog.vue'
import DocumentStatus from '../document/components/DocumentStatus.vue'
import DocumentTags from '../document/components/DocumentTags.vue'
import {
  BatchEmbeddingAction,
  BatchCancelTaskAction,
  DeleteDocumentAction,
  DocumentTagsAction,
  BatchDocumentTagsAction,
  EmbeddingDocumentAction,
  GenerateQuestionsAction,
  BatchGenerateQuestionsAction,
  DownloadDocumentAction,
  ReplaceDocumentAction,
  MigrateDocumentAction,
  SettingDocumentAction,
  BatchSettingDocumentAction,
  TokenizeDocumentAction,
  BatchTokenizeAction,
} from '../document/action-dropdown'

defineOptions({ name: 'ImageListView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const route = useRoute()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))
const { knowledge, resourceApi } = useKnowledgeDetailContext()

const canImage = (action: keyof typeof perm.knowledge.system.image) => !isWorkspaceSharedResource() && (isSystemResource() ? perm.knowledge.system.image[action]() : !isWorkspaceResource() || perm.knowledge.workspace.image[action](knowledgeId.value))

/* 图片分段详情：取首个分段，弹窗关闭后卸载。 */
const paragraphDialogRef = ref<InstanceType<typeof ParagraphDialog>>()
const selectedParagraph = ref<ParagraphItem & { source_file_id?: string }>()

function handleOpenParagraph(document: DocumentItem, column?: TableColumnCtx<DocumentItem> | null) {
  if (loading.value || operationLoading.value || selectedParagraph.value || column?.type === 'selection') return
  operationLoading.value = true
  return resourceApi.paragraph
    .getParagraphPage(knowledgeId.value, document.id, { currentPage: 1, pageSize: 1 })
    .then(async (page) => {
      const paragraph = page.records[0]
      if (!paragraph) return
      selectedParagraph.value = { ...paragraph, source_file_id: document.meta?.source_file_id as string | undefined }
      await nextTick()
      paragraphDialogRef.value?.open(paragraph)
    })
    .catch(() => {})
    .finally(() => {
      operationLoading.value = false
    })
}

/* 文档名称编辑 */
function validateDocumentName(name: string): string | undefined {
  if (/[:\\/?*\[\]]/.test(name)) {
    return '文件名称不能包含以下特殊字符：: \\ / ? * [ ]'
  }
}

function saveDocumentName(documentId: string, name: string): Promise<string> {
  return (
    resourceApi.document.putDocument?.(knowledgeId.value, documentId, { name }).then((document) => {
      // 轮询可能已替换行对象，按 ID 更新当前列表中的名称与更新时间。
      const currentDocument = documentData.value.find(({ id }) => id === documentId)
      if (currentDocument) {
        currentDocument.name = document.name
        currentDocument.update_time = document.update_time
      }
      return document.name
    }) ?? Promise.resolve(documentData.value.find(({ id }) => id === documentId)?.name ?? '')
  )
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
  const requestCommonApi = isWorkspaceResource() ? CommonApi : CommonSystemApi
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
  if (documentTagLoading.value) return
  documentTagLoading.value = true
  return resourceApi.tags
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

// 图片列表通过 resource_type: 'image' 区分，其余查询参数及响应结构与文本文档一致。
function loadDocuments(showLoading = true): Promise<void> {
  stopPolling()
  if (showLoading) loading.value = true
  return resourceApi.document
    .getDocumentPage(knowledgeId.value, paginationConfig.value, {
      resource_type: DOCUMENT_RESOURCE_TYPE.IMAGE,
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
        clearDocumentSelection()
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
  if (!canImage('edit')) return Promise.resolve(false)
  operationLoading.value = true
  return (
    resourceApi.document
      .putDocument?.(knowledgeId.value, document.id, { is_active: !document.is_active })
      .then(() => {
        MsgSuccess('操作成功')
        return refreshAfterOperation().then(() => false)
      })
      .catch(() => false) ?? Promise.resolve(false)
  ).finally(() => {
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
  void loadDocuments().catch(() => {})
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

        <template v-if="!isWorkspaceSharedResource()">
          <!-- 上传图片 -->
          <ButtonUploadImage
            v-if="canImage('create')"
            :api="resourceApi.image"
            :knowledge-id="knowledgeId"
            :file-count-limit="knowledge?.file_count_limit"
            :file-size-limit="knowledge?.file_size_limit"
            @refresh="handleSearchChange()"
          />
        </template>
      </div>
    </div>
  </Teleport>
  <MkTable
    ref="documentTableRef"
    v-loading="loading || operationLoading"
    :data="documentData"
    v-model:pagination-config="paginationConfig"
    @current-change="loadDocuments()"
    @size-change="loadDocuments()"
    @selection-change="handleSelectionChange"
    @row-click="handleOpenParagraph"
    row-class-name="cursor-pointer"
    resizable
  >
    <el-table-column type="selection" width="40" reserve-selection v-if="!isWorkspaceSharedResource()" />

    <el-table-column prop="name" label="图片名称" min-width="220" show-overflow-tooltip>
      <template #default="{ row }: { row: DocumentItem }">
        <!-- 编辑文档名称 -->
        <MkEditName
          :key="row.id"
          v-model="row.name"
          :maxlength="128"
          :validate="validateDocumentName"
          :save="(name) => saveDocumentName(row.id, name)"
          :disabled="!canImage('edit')"
        >
          <template #prefix>
            <!-- 图片 -->
            <el-image class="size-7.5" :src="getFileUrl(row.meta?.source_file_id as string | undefined)" :alt="row.name" fit="cover" />
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
        <!-- 标签快捷操作 -->
        <DocumentTags
          :api="resourceApi.tags"
          :knowledge-id="knowledgeId"
          :document="row"
          v-model:loading="operationLoading"
          @refresh="refreshAfterOperation"
          :disabled="!canImage('edit')"
        />
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
    <el-table-column label="操作" width="160" fixed="right" v-if="!isWorkspaceSharedResource()">
      <template #default="{ row }: { row: DocumentItem }">
        <div class="flex-align-center" @click.stop>
          <!-- 启用或禁用文档 -->
          <el-switch :model-value="row.is_active" v-if="canImage('edit')" size="small" :disabled="operationLoading" :before-change="() => handleChangeActive(row)" />

          <el-divider direction="vertical" class="ml-3! mr-2!" />

          <div class="flex">
            <!-- 向量化或取消向量化 -->
            <EmbeddingDocumentAction
        v-if="canImage('vector')"
              :api="resourceApi.document"
              :knowledge-id="knowledgeId"
              :document="row"
              v-model:loading="operationLoading"
              @refresh="refreshAfterOperation"
            />
            <!-- 分词索引或取消分词索引 -->
            <TokenizeDocumentAction
        v-if="canImage('token')"
              :api="resourceApi.document"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document="row"
              @refresh="refreshAfterOperation"
            />
            <!-- 更多文档操作 -->
            <MkTableMoreDropdown>
              <!-- 生成或取消生成问题 -->
              <GenerateQuestionsAction
        v-if="canImage('generate')"
                :api="resourceApi.document"
                v-model:loading="operationLoading"
                :knowledge-id="knowledgeId"
                :document="row"
                @refresh="refreshAfterOperation"
              />
              <!-- 设置当前文档的标签 -->
              <DocumentTagsAction
        v-if="canImage('tag')"
                label="标签设置"
                icon="icon_tag"
                :api="resourceApi.tags"
                :knowledge-id="knowledgeId"
                :document="row"
                v-model:loading="operationLoading"
                @refresh="refreshAfterOperation"
              />

              <!-- 文档设置 -->
              <SettingDocumentAction
        v-if="canImage('edit')"
                label="设置"
                icon="icon_setting"
                :api="resourceApi.document"
                :knowledge-id="knowledgeId"
                :document="row"
                v-model:loading="operationLoading"
                @refresh="refreshAfterOperation"
              />

              <!-- 替换图片原文件 -->
              <ReplaceDocumentAction v-if="canImage('replace')" :api="resourceApi.document" :knowledge-id="knowledgeId" :document="row" v-model:loading="operationLoading" @refresh="refreshAfterOperation" />
              <!-- 迁移文档 -->
              <MigrateDocumentAction
        v-if="canImage('migrate')"
                label="迁移"
                icon="icon_move2_outlined"
                :api="resourceApi.document"
                :knowledge-id="knowledgeId"
                :document-ids="[row.id]"
                :disabled="operationLoading"
                @refresh="refreshAfterOperation"
              />

              <!-- 下载原文档 -->
              <DownloadDocumentAction v-if="canImage('download')" :api="resourceApi.document" :knowledge-id="knowledgeId" v-model:loading="operationLoading" :document="row" />

              <!-- 删除文档 -->
              <DeleteDocumentAction
        v-if="canImage('delete')"
                divided
                icon="icon_delete-trash_outlined"
                :api="resourceApi.document"
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
    <template #footer-batch-actions>
      <!-- 批量向量化 -->
      <BatchEmbeddingAction
        v-if="canImage('vector')"
        :api="resourceApi.document"
        :knowledge-id="knowledgeId"
        :document-ids="selectedDocumentIds"
        :resource-type="DOCUMENT_RESOURCE_TYPE.IMAGE"
        v-model:loading="operationLoading"
        @refresh="refreshAfterOperation"
      />
      <!-- 批量分词索引 -->
      <BatchTokenizeAction
        v-if="canImage('token')"
        :api="resourceApi.document"
        :knowledge-id="knowledgeId"
        v-model:loading="operationLoading"
        :document-ids="selectedDocumentIds"
        @refresh="refreshAfterOperation"
      />
      <!-- 批量生成问题 -->
      <BatchGenerateQuestionsAction
        v-if="canImage('generate')"
        :api="resourceApi.document"
        v-model:loading="operationLoading"
        :knowledge-id="knowledgeId"
        :document-ids="selectedDocumentIds"
        :disabled="operationLoading"
        @refresh="refreshAfterOperation"
      />
      <!-- 批量文档设置 -->
      <BatchSettingDocumentAction
        v-if="canImage('edit')"
        label="设置"
        :api="resourceApi.document"
        :knowledge-id="knowledgeId"
        :document-ids="selectedDocumentIds"
        v-model:loading="operationLoading"
        @refresh="refreshAfterOperation"
      />
      <!-- 为选中文档批量添加标签 -->
      <BatchDocumentTagsAction
        v-if="canImage('tag')"
        label="标签设置"
        :api="resourceApi.tags"
        :knowledge-id="knowledgeId"
        :document-ids="selectedDocumentIds"
        v-model:loading="operationLoading"
        @refresh="refreshAfterOperation"
      />

      <!-- 更多批量操作 -->
      <MkDropdown class="ml-3" trigger="click" placement="bottom-end" hide-when-empty persistent>
        <!-- 展开更多批量操作 -->
        <el-button plain type="primary" class="min-w-0! w-8!">
          <MkIcon name="icon_more_outlined" />
        </el-button>
        <template #dropdown>
          <MkDropdownMenu>
            <!-- 批量迁移文档 -->
            <MigrateDocumentAction
        v-if="canImage('migrate')"
              label="迁移至"
              :api="resourceApi.document"
              :knowledge-id="knowledgeId"
              :document-ids="selectedDocumentIds"
              :disabled="operationLoading"
              @refresh="refreshAfterOperation"
            />

            <!-- 批量取消向量化 -->
            <BatchCancelTaskAction v-if="canImage('vector')"
              :api="resourceApi.document"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document-ids="selectedDocumentIds"
              :task-type="DOCUMENT_TASK_TYPE.EMBEDDING"
              label="取消向量化"
              divided
              @refresh="refreshAfterOperation"
            />
            <!-- 批量取消生成问题 -->
            <BatchCancelTaskAction v-if="canImage('generate')"
              :api="resourceApi.document"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document-ids="selectedDocumentIds"
              :task-type="DOCUMENT_TASK_TYPE.GENERATE_PROBLEM"
              label="取消生成"
              @refresh="refreshAfterOperation"
            />
            <!-- 批量删除文档 -->
            <DeleteDocumentAction
        v-if="canImage('delete')"
              :api="resourceApi.document"
              :knowledge-id="knowledgeId"
              v-model:loading="operationLoading"
              :document-ids="selectedDocumentIds"
              :resource-type="DOCUMENT_RESOURCE_TYPE.IMAGE"
              batch
              @refresh="refreshAfterOperation"
            />
          </MkDropdownMenu>
        </template>
      </MkDropdown>
    </template>
  </MkTable>
  <ParagraphDialog
    v-if="selectedParagraph"
    ref="paragraphDialogRef"
    title="图片详情"
    :readonly="!canImage('edit')"
    :knowledge-id="knowledgeId"
    :document-id="selectedParagraph.document_id"
    :source-file-id="selectedParagraph.source_file_id"
    @success="refreshAfterOperation"
    @closed="selectedParagraph = undefined"
  />
</template>
