<script setup lang="ts">
import { computed, ref } from 'vue'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { ParagraphDetail, ParagraphItem, ParagraphUpdatePayload } from '@/api/types'
import type { ParagraphQuestionDraft } from './types.ts'
import ParagraphForm from './components/ParagraphForm.vue'
import ParagraphQuestions from './components/ParagraphQuestions.vue'
import ParagraphPreview from './components/ParagraphPreview.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EditParagraphDialog' })
const props = defineProps<{
  api: typeof ParagraphApi
  knowledgeId: string
  documentId: string
}>()
const emit = defineEmits<{ success: [paragraph: ParagraphItem]; closed: [] }>()

/* 详情加载：打开时固定目标，关闭动画后由页面卸载。 */
const visible = ref(false)
const mode = ref<'edit' | 'detail'>('detail')
const dialogTitle = computed(() => (mode.value === 'edit' ? '编辑' : '分段详情'))
const paragraphDetail = ref<ParagraphDetail>()
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const targetParagraphId = ref('')
const loading = ref(false)
const detailFailed = ref(false)
const relatedQuestions = ref<ParagraphQuestionDraft[]>([])

function loadParagraphDetail() {
  if (loading.value) return
  loading.value = true
  detailFailed.value = false
  return props.api
    .getParagraphDetail(targetKnowledgeId.value, targetDocumentId.value, targetParagraphId.value)
    .then((paragraph) => {
      paragraphDetail.value = paragraph
      relatedQuestions.value = paragraph.problem_list
      paragraphForm.value = { title: paragraph.title ?? '', content: paragraph.content }
    })
    .catch(() => {
      detailFailed.value = true
    })
    .finally(() => {
      loading.value = false
    })
}

function open(paragraph: ParagraphItem, initialMode: 'edit' | 'detail' = 'detail') {
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.documentId
  targetParagraphId.value = paragraph.id
  mode.value = initialMode
  visible.value = true
  void loadParagraphDetail()
}

function close() {
  if (!loading.value) visible.value = false
}

function handleBeforeClose(done: () => void) {
  if (!loading.value) done()
}

/* 编辑与详情切换：取消丢弃正文草稿，关联问题保留即时保存结果。 */
const paragraphFormRef = ref<InstanceType<typeof ParagraphForm>>()
const paragraphForm = ref<ParagraphUpdatePayload>({ title: '', content: '' })

function handleEdit() {
  if (loading.value || !paragraphDetail.value) return
  paragraphForm.value = { title: paragraphDetail.value.title ?? '', content: paragraphDetail.value.content }
  mode.value = 'edit'
}

function handleCancelEdit() {
  if (!loading.value) mode.value = 'detail'
}

function handleSubmit() {
  if (loading.value) return
  void paragraphFormRef.value
    ?.validate()
    .then((valid) => {
      if (!valid || loading.value) return
      loading.value = true
      // 正文与问题使用独立接口，保存正文不会覆盖问题关联。
      return props.api
        .putParagraph(targetKnowledgeId.value, targetDocumentId.value, targetParagraphId.value, {
          title: paragraphForm.value.title.trim(),
          content: paragraphForm.value.content,
        })
        .then((paragraph) => {
          // 问题由独立接口更新，正文保存响应不回填问题列表，避免覆盖并行操作结果。
          paragraphDetail.value = paragraph
          mode.value = 'detail'
          MsgSuccess('保存成功')
          emit('success', paragraph)
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="dialogTitle" width="1000" align-center :before-close="handleBeforeClose" @closed="emit('closed')">
    <div v-loading="loading">
      <div class="flex h-[480px] max-h-[calc(100vh-272px)] w-full gap-4">
        <el-card v-if="mode === 'detail'" shadow="never" class="mk-paragraph-card group relative min-w-0 flex-1" body-class="flex-column h-full">
          <!-- 编辑分段标题和内容 -->
          <el-button circle class="group-hover-visible absolute! top-4 right-4 shadow-md" @click="handleEdit">
            <MkIcon name="icon_edit_outlined" />
          </el-button>
          <ParagraphPreview :paragraph="paragraphDetail" />
        </el-card>
        <div v-else class="flex-column min-h-0 min-w-0 flex-1">
          <el-scrollbar height="100%" class="min-h-0 flex-1">
            <ParagraphForm ref="paragraphFormRef" v-model="paragraphForm" :knowledge-id="targetKnowledgeId" />
          </el-scrollbar>
          <div class="mt-4 shrink-0 text-right">
            <!-- 取消编辑并返回分段详情 -->
            <el-button plain :disabled="loading" @click="handleCancelEdit">取消</el-button>
            <!-- 保存分段标题和内容 -->
            <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
          </div>
        </div>
        <!-- 关联问题 -->
        <ParagraphQuestions
          v-model="relatedQuestions"
          :api="api"
          :knowledge-id="targetKnowledgeId"
          :document-id="targetDocumentId"
          :paragraph-id="targetParagraphId"
        />
      </div>
    </div>
  </MkDialog>
</template>
