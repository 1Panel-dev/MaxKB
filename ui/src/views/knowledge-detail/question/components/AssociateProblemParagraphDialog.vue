<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type MkViewLayout from '@/components/global/mk-view-layout/index.vue'
import MkSearchList from '@/components/mk-search-list/index.vue'
import type { ParamsPage } from '@/api/admin/core/types'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import type { DocumentItem, DocumentResourceType, ParagraphItem, ProblemParagraph, ProblemParagraphReference } from '@/api/types'
import { getFileUrl } from '@/utils/common'
import { getFileIconUrl } from '@/utils/icon'
import { MsgSuccess } from '@/utils/message'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import ParagraphDialog from '@/views/document-detail/paragraph-dialog/ParagraphDialog.vue'

defineOptions({ name: 'AssociateProblemParagraphDialog' })
const emit = defineEmits<{ success: [] }>()
const { knowledgeId, resourceApi } = useKnowledgeDetailContext({ resourceScopes: ['workspace', 'system-resource', 'system-shared'] as const })

const visible = ref(false)
const documentLoading = ref(false)
const operationLoading = ref(false)
const problemIds = ref<string[]>([])
const documents = ref<DocumentItem[]>([])
const resourceType = ref<DocumentResourceType>(DOCUMENT_RESOURCE_TYPE.DOCUMENT)
const documentSearchText = ref('')
const selectedDocumentId = ref('')
const paragraphSearchText = ref('')
const paragraphs = ref<ParagraphItem[]>([])
const selectedParagraphs = ref<ProblemParagraphReference[]>([])
const detailParagraph = ref<ParagraphItem>()
const infiniteScrollRef = useTemplateRef<{ reset: () => Promise<void> }>('infiniteScrollRef')
const paragraphLayoutRef = useTemplateRef<InstanceType<typeof MkViewLayout>>('paragraphLayoutRef')
const paragraphDialogRef = useTemplateRef<InstanceType<typeof ParagraphDialog>>('paragraphDialogRef')

const isBatchAssociation = computed(() => problemIds.value.length > 1)
const selectedDocument = computed(() => documents.value.find(({ id }) => id === selectedDocumentId.value))
const selectedParagraphIds = computed(() => new Set(selectedParagraphs.value.map(({ paragraph_id }) => paragraph_id)))

function getSelectedCount(documentId: string) {
  return selectedParagraphs.value.filter(({ document_id }) => document_id === documentId).length
}

function isSelected(paragraphId: string) {
  return selectedParagraphIds.value.has(paragraphId)
}

function loadDocuments() {
  paragraphLayoutRef.value?.setScrollTop(0)
  documents.value = []
  selectedDocumentId.value = ''
  documentSearchText.value = ''
  paragraphSearchText.value = ''
  paragraphs.value = []
  return resourceApi.document.getAllDocuments(knowledgeId.value, { resource_type: resourceType.value }).then((documentList) => {
    documents.value = documentList
    selectedDocumentId.value = documentList[0]?.id ?? ''
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
  // TODO(图片联调)：核对图片资源 id 能否复用 documentId 查询分段，以及分页结果中的 id、document_id、title、content。
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

function removeSelectedParagraph(paragraphId: string) {
  selectedParagraphs.value = selectedParagraphs.value.filter(({ paragraph_id }) => paragraph_id !== paragraphId)
}

function addSelectedParagraph(paragraph: ParagraphItem) {
  selectedParagraphs.value = [...selectedParagraphs.value, { paragraph_id: paragraph.id, document_id: paragraph.document_id }]
}

function updateParagraphAssociation(paragraph: ParagraphItem, unlink: boolean) {
  if (operationLoading.value) return
  const problemId = problemIds.value[0]
  if (!problemId) return
  operationLoading.value = true
  // TODO(图片联调)：核对图片分段的关联及取消关联是否复用现有 document_id / paragraph_id 协议，成功后重新打开确认回显。
  const request = unlink
    ? resourceApi.paragraph.putUnassociateParagraphProblem(knowledgeId.value, paragraph.document_id, paragraph.id, problemId)
    : resourceApi.problem.putBatchAssociateProblems(knowledgeId.value, {
        problem_id_list: [...problemIds.value],
        paragraph_list: [{ paragraph_id: paragraph.id, document_id: paragraph.document_id }],
      })
  return request
    .then(() => {
      if (unlink) {
        removeSelectedParagraph(paragraph.id)
      } else {
        addSelectedParagraph(paragraph)
      }
      MsgSuccess(unlink ? '取消关联成功' : '关联成功')
      emit('success')
    })
    .catch(() => {
      // 请求层统一提示错误，失败时保留当前选择。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function handleAssociateParagraph(paragraph: ParagraphItem) {
  if (isSelected(paragraph.id)) return
  return updateParagraphAssociation(paragraph, false)
}

function handleUnassociateParagraph(paragraph: ParagraphItem) {
  // 批量关联提交后不支持在此弹窗批量解除关联，避免只解除首个问题的关联。
  if (isBatchAssociation.value || !isSelected(paragraph.id)) return
  return updateParagraphAssociation(paragraph, true)
}

async function handleOpenParagraphDetail(paragraph: ParagraphItem) {
  if (operationLoading.value || detailParagraph.value) return
  detailParagraph.value = paragraph
  await nextTick()
  paragraphDialogRef.value?.open(paragraph)
}

function handleParagraphDialogClosed() {
  detailParagraph.value = undefined
  const problemId = problemIds.value[0]
  if (isBatchAssociation.value || !problemId) return
  // 分段详情可修改问题关联，关闭后重新读取当前问题的关联状态。
  void resourceApi.problem.getProblemParagraphs(knowledgeId.value, problemId).then((associatedParagraphs) => {
    selectedParagraphs.value = associatedParagraphs.map(({ id, document_id }) => ({ paragraph_id: id, document_id }))
  })
}

function handleClosed() {
  problemIds.value = []
  documents.value = []
  documentSearchText.value = ''
  selectedDocumentId.value = ''
  paragraphSearchText.value = ''
  paragraphs.value = []
  selectedParagraphs.value = []
  detailParagraph.value = undefined
}

function open(targetProblemIds: string[]) {
  if (visible.value || operationLoading.value || !targetProblemIds.length) return
  const problemId = targetProblemIds[0]
  if (!problemId) return
  problemIds.value = [...targetProblemIds]
  resourceType.value = DOCUMENT_RESOURCE_TYPE.DOCUMENT
  visible.value = true
  documentLoading.value = true
  // TODO(图片联调)：确认已关联分段查询包含图片分段，并返回 id、document_id，供选中态和关联数量回显。
  const associatedParagraphs =
    targetProblemIds.length === 1 ? resourceApi.problem.getProblemParagraphs(knowledgeId.value, problemId) : Promise.resolve<ProblemParagraph[]>([])
  return Promise.all([loadDocuments(), associatedParagraphs])
    .then(([, problemParagraphs]) => {
      selectedParagraphs.value = problemParagraphs.map(({ id, document_id }) => ({ paragraph_id: id, document_id }))
    })
    .catch(() => {
      // 请求层统一提示错误，失败时保持空列表。
    })
    .finally(() => {
      documentLoading.value = false
    })
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" align-center class="mk-aside-content-dialog" width="1200" @closed="handleClosed">
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
          <MkSearchList
            v-model="documentSearchText"
            :data="documents"
            :default-active="selectedDocumentId"
            :empty-text="resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE ? '暂无图片' : '暂无文档'"
            @click="handleSelectDocument"
          >
            <template #default="{ row }">
              <!-- TODO 图片 -->
              <el-image
                v-if="resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE"
                :src="getFileUrl(row.meta?.source_file_id as string | undefined)"
                class="mr-2 size-6 shrink-0"
                :alt="row.name"
                fit="cover"
              />
              <img v-else :src="getFileIconUrl(row.name)" class="mr-2 size-4 shrink-0" alt="" />
              <span class="min-w-0 flex-1 truncate" :title="row.name">{{ row.name }}</span>
              <span v-if="getSelectedCount(row.id)" class="ml-1 flex-center h-4 min-w-4 shrink-0 rounded-full bg-primary px-1 text-xs text-white">
                {{ getSelectedCount(row.id) }}
              </span>
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
                <!-- 查看当前分段详情及其关联状态 -->
                <el-card
                  shadow="never"
                  class="mk-paragraph-card group relative cursor-pointer"
                  :class="{ active: isSelected(paragraph.id), disabled: operationLoading }"
                  @click="handleOpenParagraphDetail(paragraph)"
                >
                  <h4 class="mb-2 truncate" :title="paragraph.title || '-'">{{ paragraph.title || '-' }}</h4>
                  <p class="mb-3 line-clamp-2 break-words">{{ paragraph.content }}</p>
                  <span class="text-sm text-N500">{{ paragraph.content.length }} 字符</span>
                  <MkTooltip v-if="!isSelected(paragraph.id)" content="关联" placement="top">
                    <!-- 关联当前问题与分段 -->
                    <el-button
                      circle
                      class="group-hover-visible absolute top-2 right-2 shadow-md"
                      :disabled="operationLoading"
                      @click.stop="handleAssociateParagraph(paragraph)"
                    >
                      <MkIcon name="icon_link-record_outlined" />
                    </el-button>
                  </MkTooltip>
                  <MkTooltip v-else-if="!isBatchAssociation" content="取消关联" placement="top">
                    <!-- 取消当前问题与分段的关联 -->
                    <el-button
                      circle
                      class="group-hover-visible absolute top-2 right-2 shadow-md"
                      :disabled="operationLoading"
                      @click.stop="handleUnassociateParagraph(paragraph)"
                    >
                      <MkIcon name="icon_unlink_outlined" />
                    </el-button>
                  </MkTooltip>
                </el-card>
              </template>
            </div>
            <template #empty>
              <MkEmpty :type="paragraphSearchText ? 'search' : 'default'" description="暂无分段" />
            </template>
          </MkInfiniteScroll>
        </div>
      </template>
    </MkViewLayout>
    <template #footer>
      <div class="text-left text-sm text-N600">已关联 {{ selectedParagraphs.length }}</div>
    </template>
  </MkDialog>
  <ParagraphDialog
    v-if="detailParagraph"
    ref="paragraphDialogRef"
    title="分段详情"
    :knowledge-id="knowledgeId"
    :document-id="detailParagraph.document_id"
    @closed="handleParagraphDialogClosed"
  />
</template>
