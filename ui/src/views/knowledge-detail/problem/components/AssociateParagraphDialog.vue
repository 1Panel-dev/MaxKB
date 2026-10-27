<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import type MkViewLayout from '@/components/global/mk-view-layout/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'
import type { ParamsPage } from '@/api/admin/core/types'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import type { DocumentItem, DocumentResourceType, ParagraphItem, ProblemParagraphReference } from '@/api/types'
import { KNOWLEDGE_TYPE_KEY, KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import { MsgSuccess } from '@/utils/message'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'

defineOptions({ name: 'AssociateParagraphDialog' })
const emit = defineEmits<{ success: [] }>()
const { knowledgeId, resourceApi } = useKnowledgeDetailContext({ resourceScopes: ['workspace', 'system-resource', 'system-shared'] as const })

const visible = ref(false)
const documentLoading = ref(false)
const operationLoading = ref(false)
const problemIds = ref<string[]>([])
const documentData = ref<DocumentItem[]>([])
const resourceType = ref<DocumentResourceType>(DOCUMENT_RESOURCE_TYPE.DOCUMENT)
const documentSearchText = ref('')
const selectedDocumentId = ref('')
const paragraphSearchText = ref('')
const paragraphs = ref<ParagraphItem[]>([])
const selectedParagraphs = ref<ProblemParagraphReference[]>([])
const associatedParagraphs = ref<ProblemParagraphReference[]>([])
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const paragraphLayoutRef = useTemplateRef<InstanceType<typeof MkViewLayout>>('paragraphLayoutRef')

const selectedDocument = computed(() => documentData.value.find(({ id }) => id === selectedDocumentId.value))
const selectedParagraphIds = computed(() => new Set(selectedParagraphs.value.map(({ paragraph_id }) => paragraph_id)))
const associatedParagraphIds = computed(() => new Set(associatedParagraphs.value.map(({ paragraph_id }) => paragraph_id)))

function getSelectedCount(documentId: string) {
  return selectedParagraphs.value.filter(({ document_id }) => document_id === documentId).length
}

function isSelected(paragraphId: string) {
  return selectedParagraphIds.value.has(paragraphId)
}

function loadDocuments() {
  paragraphLayoutRef.value?.setScrollTop(0)
  documentData.value = []
  selectedDocumentId.value = ''
  documentSearchText.value = ''
  paragraphSearchText.value = ''
  paragraphs.value = []
  return resourceApi.document.getAllDocuments(knowledgeId.value, { resource_type: resourceType.value }).then((documentRecords) => {
    documentData.value = documentRecords
    selectedDocumentId.value = documentRecords[0]?.id ?? ''
  })
}

function handleResourceTypeChange() {
  documentLoading.value = true
  return loadDocuments()
    .catch(() => {
      // 请求层统一提示错误，失败时保持当前类型的空列表。
    })
    .finally(() => {
      documentLoading.value = false
    })
}

function loadParagraphPage(pagination: ParamsPage) {
  return resourceApi.paragraph.getParagraphPage(knowledgeId.value, selectedDocumentId.value, pagination, {
    title: paragraphSearchText.value.trim() || undefined,
  })
}

function refreshParagraphs() {
  paragraphLayoutRef.value?.setScrollTop(0)
  return infiniteScrollRef.value?.reset()
}

function handleSelectDocument(document: DocumentItem) {
  if (operationLoading.value || selectedDocumentId.value === document.id) return
  selectedDocumentId.value = document.id
  paragraphSearchText.value = ''
  return refreshParagraphs()
}

function handleParagraphSearch() {
  if (!selectedDocumentId.value || operationLoading.value) return
  return refreshParagraphs()
}

// 勾选仅修改草稿，确认时保存与已有关系的差异。
function handleToggleParagraph(paragraph: ParagraphItem) {
  if (operationLoading.value) return
  if (isSelected(paragraph.id)) {
    selectedParagraphs.value = selectedParagraphs.value.filter(({ paragraph_id }) => paragraph_id !== paragraph.id)
  } else {
    selectedParagraphs.value.push({ paragraph_id: paragraph.id, document_id: paragraph.document_id })
  }
}

function handleSubmit() {
  const problemId = problemIds.value[0]
  if (operationLoading.value || documentLoading.value || !problemId) return
  const paragraphReferences = selectedParagraphs.value.filter(({ paragraph_id }) => !associatedParagraphIds.value.has(paragraph_id))
  const unassociatedParagraphs = associatedParagraphs.value.filter(({ paragraph_id }) => !selectedParagraphIds.value.has(paragraph_id))
  if (!paragraphReferences.length && !unassociatedParagraphs.length) {
    visible.value = false
    return
  }
  operationLoading.value = true
  const associationRequest = paragraphReferences.length
    ? resourceApi.problem.putBatchAssociateProblems(knowledgeId.value, {
        problem_id_list: [...problemIds.value],
        paragraph_list: paragraphReferences,
      })
    : Promise.resolve()
  return associationRequest
    .then(async () => {
      // 每次成功后更新关系快照，部分失败重试时不重复提交已完成的操作。
      associatedParagraphs.value.push(...paragraphReferences)
      for (const { document_id, paragraph_id } of unassociatedParagraphs) {
        await resourceApi.paragraph.putUnassociateParagraphProblem(knowledgeId.value, document_id, paragraph_id, problemId).then(() => {
          associatedParagraphs.value = associatedParagraphs.value.filter((paragraph) => paragraph.paragraph_id !== paragraph_id)
        })
      }
    })
    .then(() => {
      MsgSuccess('保存成功')
      visible.value = false
      emit('success')
    })
    .catch(() => {
      // 请求层统一提示错误，失败时保留本次选择以便重试。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function open(targetProblemIds: string[]) {
  if (visible.value || operationLoading.value || !targetProblemIds[0]) return
  problemIds.value = [...targetProblemIds]
  visible.value = true
  documentLoading.value = true
  return Promise.all([
    loadDocuments(),
    targetProblemIds.length === 1 ? resourceApi.problem.getProblemDetail(knowledgeId.value, targetProblemIds[0]) : [],
  ])
    .then(([, problemParagraphs]) => {
      associatedParagraphs.value = problemParagraphs.map(({ id, document_id }) => ({ paragraph_id: id, document_id }))
      selectedParagraphs.value = [...associatedParagraphs.value]
    })
    .catch(() => {
      // 请求层统一提示错误，失败时保持空列表。
    })
    .finally(() => {
      documentLoading.value = false
    })
}

function handleClosed() {
  problemIds.value = []
  documentData.value = []
  documentSearchText.value = ''
  selectedDocumentId.value = ''
  paragraphSearchText.value = ''
  paragraphs.value = []
  selectedParagraphs.value = []
  associatedParagraphs.value = []
  resourceType.value = DOCUMENT_RESOURCE_TYPE.DOCUMENT
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" class="mk-aside-content-dialog" width="1200" @closed="handleClosed">
    <template #header="{ titleId }">
      <h4 :id="titleId">关联分段</h4>
    </template>
    <MkViewLayout ref="paragraphLayoutRef" title="">
      <template #aside>
        <div v-loading="documentLoading" class="flex-column h-full min-h-0 pt-4" :inert="operationLoading">
          <!-- 切换文档或图片资源 -->
          <el-tabs
            v-model="resourceType"
            class="mx-4 mb-4"
            :before-leave="() => !documentLoading && !operationLoading"
            @tab-change="handleResourceTypeChange"
          >
            <el-tab-pane label="文档" :name="DOCUMENT_RESOURCE_TYPE.DOCUMENT" />
            <el-tab-pane label="图片" :name="DOCUMENT_RESOURCE_TYPE.IMAGE" />
          </el-tabs>
          <!-- 搜索并切换候选分段所在资源 -->
          <MkSearchList v-model="documentSearchText" :data="documentData" :default-active="selectedDocumentId" @click="handleSelectDocument">
            <template #default="{ row }">
              <div class="flex-align-center gap-2 min-w-0">
                <el-image
                  v-if="resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE"
                  :src="getFileUrl(row.meta?.source_file_id as string | undefined)"
                  class="size-6 shrink-0"
                  :alt="row.name"
                  fit="cover"
                />
                <img
                  v-else-if="KNOWLEDGE_TYPE_MAP[row.type] === KNOWLEDGE_TYPE_KEY.WEB"
                  src="@/assets/file-type/web-link-icon.svg"
                  alt=""
                  class="size-4"
                />
                <img v-else :src="getFileIconUrl(row.name)" class="size-4 shrink-0" alt="" />
                <span class="min-w-0 flex-1 truncate" :title="row.name">{{ row.name }}</span>
                <!-- 关联数字 -->
                <span v-if="getSelectedCount(row.id)" class="mk-badge">
                  {{ getSelectedCount(row.id) }}
                </span>
              </div>
            </template>
          </MkSearchList>
        </div>
      </template>

      <template #default="{ Header }">
        <component :is="Header">
          <span class="min-w-0 truncate" :title="selectedDocument?.name">{{ selectedDocument?.name || '-' }}</span>
          <MkSearchInput v-model="paragraphSearchText" class="w-60! shrink-0" :disabled="!selectedDocument" @change="handleParagraphSearch" />
        </component>
        <div v-loading="operationLoading" class="flex-column min-h-0 flex-1">
          <MkInfiniteScroll
            v-if="selectedDocument && !documentLoading"
            ref="infiniteScrollRef"
            v-model="paragraphs"
            class="flex-1"
            :load="loadParagraphPage"
          >
            <div class="space-y-2">
              <template v-for="paragraph in paragraphs" :key="paragraph.id">
                <!-- 勾选或取消本次批量关联的分段 -->
                <el-card
                  shadow="never"
                  class="mk-paragraph-card group relative cursor-pointer"
                  :class="{ active: isSelected(paragraph.id), disabled: operationLoading }"
                  @click="handleToggleParagraph(paragraph)"
                >
                  <!-- 勾选当前分段用于批量关联 -->
                  <el-checkbox
                    class="absolute! top-4 right-4"
                    :model-value="isSelected(paragraph.id)"
                    @click.stop
                    @change="handleToggleParagraph(paragraph)"
                  />

                  <el-image
                    v-if="resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE"
                    class="w-fit [&_img]:size-auto! [&_img]:max-h-50 mb-2"
                    :src="getFileUrl(selectedDocument.meta?.source_file_id as string | undefined)"
                    :alt="selectedDocument.name"
                    fit="contain"
                  />

                  <h4 class="mb-2">{{ paragraph.title || '-' }}</h4>
                  <MdPreview :model-value="paragraph.content" />
                  <p class="mt-2 text-sm text-N600">{{ paragraph.content.length }} 字符</p>
                </el-card>
              </template>
            </div>
            <template #empty>
              <MkEmpty :type="paragraphSearchText ? 'search' : 'default'" description="暂无分段" />
            </template>
          </MkInfiniteScroll>
          <el-empty v-else-if="!documentLoading" class="flex-1" description="暂无数据" />
        </div>
      </template>
    </MkViewLayout>
    <template #footer>
      <div class="flex-between">
        <div class="text-sm text-N600">已选择 {{ selectedParagraphs.length }}</div>
        <div>
          <!-- 取消本次批量关联 -->
          <el-button plain :disabled="operationLoading || documentLoading" @click="visible = false">取消</el-button>
          <!-- 确认批量关联所选分段 -->
          <el-button type="primary" :loading="operationLoading" @click="handleSubmit">确认</el-button>
        </div>
      </div>
    </template>
  </MkDialog>
</template>
