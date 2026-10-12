<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type MkViewLayout from '@/components/global/mk-view-layout/index.vue'
import DocumentApi from '@/api/admin/workspace/knowledge/document'
import ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { DocumentItem, ParagraphCreatePayload, ParagraphItem, ParagraphQuery } from '@/api/types'
import { getFileIconUrl } from '@/utils/icon'
import { MsgSuccess } from '@/utils/message'
import CreateParagraphDialog from './CreateParagraphDialog.vue'

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
    .then((records) => {
      paragraphs.value = records
      selectedParagraphIds.value = []
      activeParagraphId.value = records[0]?.id ?? ''
      layoutRef.value?.setScrollTop(0)
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
const activeParagraphId = ref('')

function getParagraphElements() {
  return layoutRef.value?.getScrollContainer()?.querySelectorAll<HTMLElement>('[data-paragraph-id]')
}

function handleSelectParagraph(paragraphId: string) {
  const container = layoutRef.value?.getScrollContainer()
  const paragraphElement = Array.from(getParagraphElements() ?? []).find((element) => element.dataset.paragraphId === paragraphId)
  if (!container || !paragraphElement) return
  activeParagraphId.value = paragraphId
  layoutRef.value?.setScrollTop(container.scrollTop + paragraphElement.getBoundingClientRect().top - container.getBoundingClientRect().top)
}

function handleScroll() {
  const container = layoutRef.value?.getScrollContainer()
  const paragraphElements = getParagraphElements()
  if (!container || !paragraphElements?.length) return
  const containerTop = container.getBoundingClientRect().top
  let currentId = paragraphs.value[0]?.id ?? ''
  for (const element of paragraphElements) {
    if (element.getBoundingClientRect().top > containerTop + 24) break
    currentId = element.dataset.paragraphId ?? currentId
  }
  activeParagraphId.value = currentId
}

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

/* 新增成功后清空搜索并重新查询服务端顺序，避免重复创建。 */
const createDialogMounted = ref(false)
const createDialogRef = ref<InstanceType<typeof CreateParagraphDialog>>()
const saving = ref(false)
const searchKey = ref(0)

async function handleOpenCreateParagraph() {
  createDialogMounted.value = true
  await nextTick()
  createDialogRef.value?.open()
}

function handleCreateParagraph(payload: ParagraphCreatePayload) {
  if (saving.value) return
  saving.value = true
  return ParagraphApi.postParagraph(knowledgeId.value, documentId.value, payload)
    .then(() => {
      createDialogRef.value?.close()
      MsgSuccess('添加成功')
      paragraphQuery.value = {}
      searchKey.value += 1
      return loadParagraphs()
    })
    .catch(() => {})
    .finally(() => {
      saving.value = false
    })
}

watch(
  [knowledgeId, documentId],
  () => {
    documentDetail.value = undefined
    paragraphs.value = []
    paragraphQuery.value = {}
    searchKey.value += 1
    batchMode.value = false
    void Promise.all([
      DocumentApi.getDocumentDetail(knowledgeId.value, documentId.value).then((document) => {
        documentDetail.value = document
      }),
      loadParagraphs(),
    ]).catch(() => {})
  },
  { immediate: true },
)
</script>

<template>
  <MkViewLayout ref="layoutRef" title="" :loading="loading" @scroll="handleScroll">
    <template #top>
      <div class="flex-between gap-4">
        <div class="flex-align-center min-w-0 gap-3">
          <!-- 返回文档列表 -->
          <el-button text title="返回文档列表" @click="handleBack"><MkIcon name="icon_arrow-left_outlined" :size="24" /></el-button>
          <img v-if="documentDetail" :src="getFileIconUrl(documentDetail.name)" alt="" class="size-6 shrink-0" />
          <h4 class="truncate" :title="documentDetail?.name">{{ documentDetail?.name ?? '文档分段' }}</h4>
        </div>
        <div class="flex-align-center shrink-0 gap-3">
          <MkComplexSearch :key="searchKey" :fields="searchFields" @change="handleSearchChange" />
          <!-- 切换批量选择 -->
          <el-button :type="batchMode ? 'primary' : 'default'" plain @click="handleToggleBatchMode">批量选择</el-button>
          <!-- 添加文档分段 -->
          <el-button type="primary" :disabled="saving" @click="handleOpenCreateParagraph">
            <MkIcon name="icon_add_outlined" class="mr-1" />
            添加分段
          </el-button>
        </div>
      </div>
    </template>
    <template #aside>
      <el-scrollbar class="min-h-0 flex-1" view-class="p-4">
        <template v-for="(paragraph, index) in paragraphs" :key="paragraph.id">
          <!-- 定位文档分段 -->
          <button
            type="button"
            class="block w-full cursor-pointer truncate rounded-md px-2 py-2 text-left hover:text-primary"
            :class="activeParagraphId === paragraph.id ? 'text-primary' : 'text-N600'"
            :title="`${index + 1}、${paragraph.title || '无标题分段'}`"
            @click="handleSelectParagraph(paragraph.id)"
          >
            {{ index + 1 }}、{{ paragraph.title || '无标题分段' }}
          </button>
        </template>
      </el-scrollbar>
    </template>
    <template #default="{ Header, Footer }">
      <component :is="Header">
        <p class="text-N600">{{ paragraphs.length }} 分段</p>
      </component>
      <div class="space-y-3">
        <template v-for="(paragraph, index) in paragraphs" :key="paragraph.id">
          <article :data-paragraph-id="paragraph.id" class="rounded-xl border p-4">
            <div class="mb-3 flex-between gap-3">
              <h4>{{ index + 1 }}、{{ paragraph.title || '无标题分段' }}</h4>
              <el-checkbox
                v-if="batchMode"
                :model-value="selectedParagraphIds.includes(paragraph.id)"
                :value="paragraph.id"
                :title="`选择第 ${index + 1} 个分段`"
                @change="(selected: boolean | string | number) => handleSelectBatchParagraph(paragraph.id, Boolean(selected))"
              />
            </div>
            <MdPreview :model-value="paragraph.content" />
          </article>
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
        <template #footer-batch-actions></template>
      </component>
    </template>
  </MkViewLayout>
  <CreateParagraphDialog
    v-if="createDialogMounted"
    ref="createDialogRef"
    :loading="saving"
    @submit="handleCreateParagraph"
    @closed="createDialogMounted = false"
  />
</template>
