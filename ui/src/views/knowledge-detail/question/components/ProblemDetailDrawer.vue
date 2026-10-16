<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { ProblemItem, ProblemParagraph } from '@/api/types'
import MkEditName from '@/components/mk-edit-name/index.vue'
import { MsgSuccess } from '@/utils/message'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { useDocumentDetailContext } from '@/views/document-detail/context'
import ParagraphDialog from '@/views/document-detail/paragraph-dialog/ParagraphDialog.vue'
import ProblemParagraphCard from './ProblemParagraphCard.vue'

defineOptions({ name: 'ProblemDetailDrawer' })
const problem = defineModel<ProblemItem>({ required: true })
const props = defineProps<{ hasPrevious: boolean; hasNext: boolean; listLoading: boolean }>()
const emit = defineEmits<{ previous: []; next: []; refresh: []; closed: [] }>()
const { knowledgeId, resourceApi } = useKnowledgeDetailContext()
const { resourceApi: documentResourceApi } = useDocumentDetailContext()
const visible = ref(true)
const loading = ref(false)
const loadFailed = ref(false)
const paragraphs = ref<ProblemParagraph[]>([])
const selectedParagraph = ref<ProblemParagraph>()
const paragraphDialogRef = ref<InstanceType<typeof ParagraphDialog>>()
const busy = computed(() => loading.value || props.listLoading)

function loadParagraphs() {
  loadFailed.value = false
  return (
    resourceApi.problem.getProblemParagraphs?.(knowledgeId.value, problem.value.id).then((records) => {
      paragraphs.value = records
      problem.value.paragraph_count = records.length
    }) ?? Promise.resolve()
  ).catch(() => {
    loadFailed.value = true
  })
}

function handleLoadParagraphs() {
  loading.value = true
  return loadParagraphs().finally(() => {
    loading.value = false
  })
}

function handleSaveProblem(content: string): Promise<string> {
  loading.value = true
  return (
    resourceApi.problem.putProblem?.(knowledgeId.value, problem.value.id, content).then(() => {
      MsgSuccess('修改成功')
      emit('refresh')
      return content
    }) ?? Promise.reject(new Error('Problem editing is unavailable'))
  ).finally(() => {
    loading.value = false
  })
}

function handleUnlinkParagraph(paragraph: ProblemParagraph) {
  if (busy.value) return
  loading.value = true
  return (
    documentResourceApi.paragraph
      .putUnassociateParagraphProblem?.(knowledgeId.value, paragraph.document_id, paragraph.id, problem.value.id)
      .then(() => {
        MsgSuccess('取消关联成功')
        emit('refresh')
        return loadParagraphs()
      }) ?? Promise.resolve()
  )
    .catch(() => {
      // 请求层提示错误，失败时保留当前关联。
    })
    .finally(() => {
      loading.value = false
    })
}

async function handleOpenParagraph(paragraph: ProblemParagraph) {
  if (busy.value) return
  selectedParagraph.value = paragraph
  // 先挂载带有当前文档 ID 的详情弹窗，再调用其已有打开方法。
  await nextTick()
  paragraphDialogRef.value?.open(paragraph)
}

function handleParagraphClosed() {
  selectedParagraph.value = undefined
  // 分段详情也能修改问题关联，关闭后重新读取关联与列表计数。
  emit('refresh')
  void handleLoadParagraphs()
}

function handleBeforeClose(done: () => void) {
  if (!busy.value) done()
}

watch(
  () => problem.value.id,
  () => {
    paragraphs.value = []
    void handleLoadParagraphs()
  },
  { immediate: true },
)
</script>

<template>
  <MkDrawer v-model="visible" title="问题详情" size="860" :before-close="handleBeforeClose" @closed="emit('closed')">
    <div v-loading="loading">
      <div class="mb-4">
        <div class="mb-2">问题</div>
        <MkEditName :key="problem.id" v-model="problem.content" :maxlength="256" :save="handleSaveProblem" :title="problem.content" />
      </div>
      <div class="mb-2">关联分段数（{{ problem.paragraph_count }}）</div>
      <div v-if="paragraphs.length" class="flex-column gap-3">
        <template v-for="paragraph in paragraphs" :key="paragraph.id">
          <ProblemParagraphCard :paragraph="paragraph" :disabled="busy" @open="handleOpenParagraph" @unlink="handleUnlinkParagraph" />
        </template>
      </div>
      <MkEmpty v-else-if="!loading" description="暂无关联分段" />
    </div>
    <template #footer>
      <!-- 关联分段：TODO -->
      <el-button plain>关联分段</el-button>
      <!-- 查看上一个问题 -->
      <el-button plain :disabled="busy || !hasPrevious" @click="emit('previous')">上一个</el-button>
      <!-- 查看下一个问题 -->
      <el-button plain :disabled="busy || !hasNext" @click="emit('next')">下一个</el-button>
    </template>
  </MkDrawer>
  <ParagraphDialog
    v-if="selectedParagraph"
    ref="paragraphDialogRef"
    title="分段详情"
    :knowledge-id="knowledgeId"
    :document-id="selectedParagraph.document_id"
    @closed="handleParagraphClosed"
  />
</template>
