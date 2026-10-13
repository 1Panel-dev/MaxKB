<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { ElAnchor } from 'element-plus'
import type MkViewLayout from '@/components/global/mk-view-layout/index.vue'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { DocumentItem, ParagraphItem, ParagraphQuery } from '@/api/types'
import { getFileIconUrl } from '@/utils/icon'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import CreateParagraphDialog from './paragraph-dialog/CreateParagraphDialog.vue'
import EditParagraphDialog from './paragraph-dialog/ParagraphDialog.vue'
import ButtonMigrateParagraph from './migrate/ButtonMigrateParagraph.vue'
import ButtonGenerateQuestions from './components/ButtonGenerateQuestions.vue'

defineOptions({ name: 'KnowledgeParagraphView' })

/* 文档详情与分段查询 */
const route = useRoute()
const router = useRouter()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))
const documentId = computed(() => String(route.params.documentId ?? ''))
const documentDetail = ref<DocumentItem>()
const paragraphs = ref<ParagraphItem[]>([])
const loading = ref(false)
const paragraphQuery = ref<ParagraphQuery>({})
const searchFields = [
  { label: '标题', value: 'title' },
  { label: '内容', value: 'content' },
]

function loadParagraphs() {
  loading.value = true
  return ParagraphApi.getParagraphList(knowledgeId.value, documentId.value, paragraphQuery.value)
    .then(async (records) => {
      paragraphs.value = records
      selectedParagraphIds.value = []
      await nextTick()
      layoutRef.value?.setScrollTop(0)
      if (records[0]) paragraphAnchorRef.value?.scrollTo(`#paragraph-${records[0].id}`)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange(query?: ParagraphQuery) {
  paragraphQuery.value = query ?? {}
  void loadParagraphs().catch(() => {})
}

function handleBack() {
  void router.push({
    name: 'workspace-knowledge-document-list',
    params: { workspaceId: route.params.workspaceId, knowledgeId: knowledgeId.value, type: route.params.type },
    query: route.query,
  })
}

/* 分段目录定位与滚动高亮 */
const layoutRef = ref<InstanceType<typeof MkViewLayout>>()
const paragraphAnchorRef = ref<InstanceType<typeof ElAnchor>>()
const paragraphScrollContainer = computed(() => layoutRef.value?.getScrollContainer())

/* 批量选择当前查询结果 */
const batchMode = ref(false)
const selectedParagraphIds = ref<string[]>([])
const paragraphIds = computed(() => paragraphs.value.map(({ id }) => id))

function handleToggleBatchMode() {
  batchMode.value = !batchMode.value
  selectedParagraphIds.value = []
}

function handleSelectBatchParagraph(paragraphId: string, selected: boolean) {
  selectedParagraphIds.value = selected ? [...selectedParagraphIds.value, paragraphId] : selectedParagraphIds.value.filter((id) => id !== paragraphId)
}

function handleClickParagraphCard(paragraph: ParagraphItem) {
  if (batchMode.value) {
    handleSelectBatchParagraph(paragraph.id, !selectedParagraphIds.value.includes(paragraph.id))
    return
  }
  return handleOpenParagraphDetail(paragraph)
}

// 迁移、删除成功后仅移除本次操作的分段，不重新查询接口。
async function handleRemoveParagraphs(removedParagraphIds: string[]) {
  const removedIds = new Set(removedParagraphIds)
  paragraphs.value = paragraphs.value.filter(({ id }) => !removedIds.has(id))
  selectedParagraphIds.value = []
  await nextTick()
  layoutRef.value?.setScrollTop(0)
  if (paragraphs.value[0]) paragraphAnchorRef.value?.scrollTo(`#paragraph-${paragraphs.value[0].id}`)
}

// 生成问题成功后重新查询当前筛选结果。
function handleGenerateQuestionsSuccess() {
  selectedParagraphIds.value = []
  return loadParagraphs().catch(() => {})
}

// 批量删除：确认前固定目标，取消或失败保留勾选。
const deleteConfirming = ref(false)
const deleting = ref(false)

function handleBatchDeleteParagraphs() {
  if (loading.value || deleteConfirming.value || deleting.value || !selectedParagraphIds.value.length) return
  const targetParagraphIds = [...selectedParagraphIds.value]
  const targetKnowledgeId = knowledgeId.value
  const targetDocumentId = documentId.value
  deleteConfirming.value = true
  return MsgConfirm(`确认删除选中的 ${targetParagraphIds.length} 个分段？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      deleting.value = true
      return ParagraphApi.putBatchDeleteParagraphs(targetKnowledgeId, targetDocumentId, targetParagraphIds).then(() => {
        MsgSuccess('删除成功')
        return handleRemoveParagraphs(targetParagraphIds)
      })
    })
    .catch(() => {
      // 取消无需提示，请求失败由请求层统一提示。
    })
    .finally(() => {
      deleteConfirming.value = false
      deleting.value = false
    })
}

/* 分段弹窗按需挂载；新增后清空搜索，编辑后保留当前筛选。 */
const createDialogMounted = ref(false)
const createDialogRef = ref<InstanceType<typeof CreateParagraphDialog>>()
const editDialogMounted = ref(false)
const editDialogRef = ref<InstanceType<typeof EditParagraphDialog>>()
const searchKey = ref(0)

async function handleOpenCreateParagraph() {
  createDialogMounted.value = true
  await nextTick()
  createDialogRef.value?.open()
}

async function handleOpenParagraphDetail(paragraph: ParagraphItem) {
  editDialogMounted.value = true
  await nextTick()
  editDialogRef.value?.open(paragraph)
}

function handleParagraphSuccess(mode: 'create' | 'edit') {
  if (mode === 'create') {
    paragraphQuery.value = {}
    searchKey.value += 1
  }
  return loadParagraphs().catch(() => {})
}

onMounted(() => {
  void Promise.all([
    DocumentApi.getDocumentDetail(knowledgeId.value, documentId.value).then((document) => {
      documentDetail.value = document
    }),
    loadParagraphs(),
  ]).catch(() => {})
})
</script>

<template>
  <MkViewLayout ref="layoutRef" title="" :loading="loading" collapsible class="[&_aside+button]:top-4!">
    <template #top>
      <div class="flex-between gap-4">
        <div class="flex-align-center min-w-0 gap-2">
          <!-- 返回文档列表 -->
          <el-button text @click="handleBack"><MkIcon name="icon_arrow-left_outlined" :size="20" /></el-button>
          <img v-if="documentDetail" :src="getFileIconUrl(documentDetail.name)" alt="" class="size-6 shrink-0" />
          <h4 class="truncate" :title="documentDetail?.name">{{ documentDetail?.name ?? '文档分段' }}</h4>
        </div>
        <div class="flex-align-center shrink-0 gap-3">
          <MkComplexSearch :key="searchKey" :fields="searchFields" @change="handleSearchChange" />
          <!-- 切换批量选择 -->
          <span>
            <el-button :type="batchMode ? 'primary' : undefined" :disabled="!paragraphs.length" plain @click="handleToggleBatchMode">
              <MkIcon name="icon_Batch_outlined" />
              <span>{{ batchMode ? '取消选择' : '批量选择' }}</span>
            </el-button>
          </span>
          <!-- 添加文档分段 -->
          <el-button v-if="!batchMode" type="primary" @click="handleOpenCreateParagraph">
            <MkIcon name="icon_add_outlined" />
            <span>添加分段</span>
          </el-button>
        </div>
      </div>
    </template>
    <template #aside>
      <el-scrollbar class="min-h-0 flex-1" view-class="p-4">
        <el-anchor
          v-if="paragraphScrollContainer && paragraphs.length"
          ref="paragraphAnchorRef"
          :container="paragraphScrollContainer"
          :marker="false"
          :offset="24"
          select-scroll-top
          @click.prevent
        >
          <!-- 定位文档分段 -->
          <el-anchor-link v-for="paragraph in paragraphs" :key="paragraph.id" :href="`#paragraph-${paragraph.id}`">
            <div
              class="truncate rounded-md px-2 py-1 font-normal text-N600 hover:bg-N900/10 [.is-active_&]:text-primary"
              :title="paragraph.title || ''"
            >
              {{ paragraph.title || '-' }}
            </div>
          </el-anchor-link>
        </el-anchor>
      </el-scrollbar>
    </template>
    <template #default="{ Header, Footer }">
      <component :is="Header">
        <p class="text-N600">{{ paragraphs.length }} 分段</p>
      </component>
      <div class="space-y-3">
        <template v-for="paragraph in paragraphs" :key="paragraph.id">
          <el-card
            :id="`paragraph-${paragraph.id}`"
            shadow="never"
            class="mk-paragraph-card group relative cursor-pointer"
            :class="{ selectable: batchMode, active: batchMode && selectedParagraphIds.includes(paragraph.id) }"
            @click="handleClickParagraphCard(paragraph)"
          >
            <h4 class="mb-2">{{ paragraph.title || '-' }}</h4>

            <!-- 选择批量操作的分段 -->
            <el-checkbox
              v-if="batchMode"
              class="absolute! top-4 right-4"
              :model-value="selectedParagraphIds.includes(paragraph.id)"
              @click.stop
              @change="(selected: boolean | string | number) => handleSelectBatchParagraph(paragraph.id, Boolean(selected))"
            />

            <MdPreview :model-value="paragraph.content" />
          </el-card>
        </template>
      </div>
      <MkEmpty v-if="!loading && !paragraphs.length" :type="Object.keys(paragraphQuery).length ? 'search' : 'default'" description="暂无分段" />
      <component
        :is="Footer"
        v-if="batchMode"
        v-model:batch-selection="selectedParagraphIds"
        :batch-values="paragraphIds"
        @batch-cancel="batchMode = false"
      >
        <template #footer-batch-actions>
          <!-- 批量迁移分段 -->
          <ButtonMigrateParagraph
            :api="ParagraphApi"
            :knowledge-id="knowledgeId"
            :document-id="documentId"
            :paragraph-ids="selectedParagraphIds"
            :disabled="loading"
            @success="handleRemoveParagraphs"
          />
          <!-- 批量生成问题 -->
          <ButtonGenerateQuestions
            :api="ParagraphApi"
            :knowledge-id="knowledgeId"
            :document-id="documentId"
            :paragraph-ids="selectedParagraphIds"
            :disabled="loading"
            @refresh="handleGenerateQuestionsSuccess"
          />
          <!-- 批量删除分段 -->
          <el-button
            type="danger"
            plain
            :loading="deleting"
            :disabled="loading || deleteConfirming || !selectedParagraphIds.length"
            @click="handleBatchDeleteParagraphs"
          >
            删除
          </el-button>
        </template>
      </component>
    </template>
  </MkViewLayout>
  <CreateParagraphDialog
    v-if="createDialogMounted"
    ref="createDialogRef"
    :api="ParagraphApi"
    :knowledge-id="knowledgeId"
    :document-id="documentId"
    @success="handleParagraphSuccess"
    @closed="createDialogMounted = false"
  />
  <EditParagraphDialog
    v-if="editDialogMounted"
    ref="editDialogRef"
    :api="ParagraphApi"
    :knowledge-id="knowledgeId"
    :document-id="documentId"
    @success="handleParagraphSuccess"
    @closed="editDialogMounted = false"
  />
</template>
