<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import type { ProblemItem, ProblemParagraph } from '@/api/types'
import MkEditName from '@/components/mk-edit-name/index.vue'
import { MsgSuccess } from '@/utils/message'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { useDocumentDetailContext } from '@/views/document-detail/context'
import ParagraphDialog from '@/views/document-detail/paragraph-dialog/ParagraphDialog.vue'
import { getFileIconUrl } from '@/utils/icon'

defineOptions({ name: 'ProblemDetailDrawer' })
const problem = defineModel<ProblemItem>({ required: true })
defineProps<{ hasPrevious: boolean; hasNext: boolean }>()
const emit = defineEmits<{ previous: []; next: []; refresh: []; closed: []; associate: [] }>()
const { knowledgeId, resourceApi } = useKnowledgeDetailContext()
const { resourceApi: documentResourceApi } = useDocumentDetailContext()
const visible = ref(true)
const loading = ref(false)
const loadFailed = ref(false)
const paragraphs = ref<ProblemParagraph[]>([])
const selectedParagraph = ref<ProblemParagraph>()
const paragraphDialogRef = ref<InstanceType<typeof ParagraphDialog>>()

function loadParagraphs() {
  loadFailed.value = false
  return (
    resourceApi.problem.getProblemDetail?.(knowledgeId.value, problem.value.id).then((records) => {
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
  if (loading.value) return
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
  if (loading.value) return
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
  if (!loading.value) done()
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
          <!-- 查看关联分段详情 -->
          <el-card class="mk-paragraph-card group relative cursor-pointer" shadow="never" @click="handleOpenParagraph(paragraph)">
            <!-- 取消当前问题与分段的关联，不删除分段 -->
            <MkTooltip content="取消关联" placement="top">
              <el-button
                circle
                class="group-hover-visible absolute top-3 right-3 shadow-md"
                :disabled="loading"
                @click.stop="handleUnlinkParagraph(paragraph)"
              >
                <MkIcon name="icon_unlink_outlined" />
              </el-button>
            </MkTooltip>

            <h4 class="mb-2">{{ paragraph.title || '-' }}</h4>
            <MdPreview :model-value="paragraph.content" />
            <div class="flex-align-center gap-2 text-sm text-N600">
              <span class="shrink-0">{{ paragraph.content.length }} 字符</span>
              <el-divider direction="vertical" />
              <img :src="getFileIconUrl(paragraph.document_name)" class="size-4 shrink-0" alt="" />
              <span class="truncate" :title="paragraph.document_name">{{ paragraph.document_name }}</span>
            </div>
          </el-card>
        </template>
      </div>
      <MkEmpty v-else-if="!loading" description="暂无关联分段" />
    </div>
    <template #footer>
      <!-- 关联当前问题的分段 -->
      <el-button plain :disabled="loading" @click="emit('associate')">关联分段</el-button>
      <!-- 查看上一个问题 -->
      <el-button plain :disabled="loading || !hasPrevious" @click="emit('previous')">上一个</el-button>
      <!-- 查看下一个问题 -->
      <el-button plain :disabled="loading || !hasNext" @click="emit('next')">下一个</el-button>
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
