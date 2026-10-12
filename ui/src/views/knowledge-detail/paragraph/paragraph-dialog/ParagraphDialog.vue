<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { ParagraphDetail, ParagraphItem, ParagraphUpdatePayload } from '@/api/types'
import type { ParagraphQuestionDraft } from './types.ts'
import ParagraphForm from './components/ParagraphForm.vue'
import ParagraphQuestions from './components/ParagraphQuestions.vue'
import ParagraphPreview from './components/ParagraphPreview.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EditParagraphDialog' })
const props = withDefaults(
  defineProps<{
    api: typeof ParagraphApi
    knowledgeId: string
    documentId: string
    disabled?: boolean
  }>(),
  { disabled: false },
)
const emit = defineEmits<{ success: [mode: 'edit']; closed: [] }>()

/* 详情加载：打开时固定目标，关闭动画后由页面卸载。 */
const visible = ref(false)
const mode = ref<'edit' | 'detail'>('detail')
const dialogTitle = computed(() => (mode.value === 'edit' ? '编辑' : '分段详情'))
const paragraphDetail = ref<ParagraphDetail>()
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const targetParagraphId = ref('')
const detailLoading = ref(false)
const detailFailed = ref(false)
const saving = ref(false)
const questionAdding = ref(false)
const questionLoading = ref(false)
const relatedQuestions = ref<ParagraphQuestionDraft[]>([])
const busy = computed(() => detailLoading.value || saving.value || questionLoading.value)

function loadParagraphDetail() {
  if (detailLoading.value) return
  detailLoading.value = true
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
      detailLoading.value = false
    })
}

function open(paragraph: ParagraphItem, initialMode: 'edit' | 'detail' = 'detail') {
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.documentId
  targetParagraphId.value = paragraph.id
  mode.value = props.disabled ? 'detail' : initialMode
  visible.value = true
  void loadParagraphDetail()
}

function close() {
  if (!busy.value) visible.value = false
}

function handleBeforeClose(done: () => void) {
  if (!busy.value) done()
}

/* 编辑与详情切换：取消丢弃正文草稿，关联问题保留即时保存结果。 */
const paragraphFormRef = ref<InstanceType<typeof ParagraphForm>>()
const paragraphForm = ref<ParagraphUpdatePayload>({ title: '', content: '' })

function handleEdit() {
  if (props.disabled || busy.value || !paragraphDetail.value) return
  paragraphForm.value = { title: paragraphDetail.value.title ?? '', content: paragraphDetail.value.content }
  mode.value = 'edit'
}

function handleCancelEdit() {
  if (!busy.value) mode.value = 'detail'
}

// 父级切换为只读时立即回到详情，防止继续编辑和保存。
watch(
  () => props.disabled,
  (disabled) => {
    if (disabled) mode.value = 'detail'
  },
)

function handleSubmit() {
  if (props.disabled || busy.value || questionAdding.value) return
  void paragraphFormRef.value
    ?.validate()
    .then((valid) => {
      if (!valid || props.disabled || busy.value || questionAdding.value) return
      saving.value = true
      // 正文与问题使用独立接口，保存正文不会覆盖问题关联。
      return props.api
        .putParagraph(targetKnowledgeId.value, targetDocumentId.value, targetParagraphId.value, {
          title: paragraphForm.value.title.trim(),
          content: paragraphForm.value.content,
        })
        .then((paragraph) => {
          paragraphDetail.value = paragraph
          relatedQuestions.value = paragraph.problem_list
          mode.value = 'detail'
          MsgSuccess('保存成功')
          emit('success', 'edit')
        })
        .finally(() => {
          saving.value = false
        })
    })
    .catch(() => {})
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="dialogTitle" width="1000" align-center :before-close="handleBeforeClose" @closed="emit('closed')">
    <div v-loading="detailLoading || saving">
      <div class="flex">
        <ParagraphPreview v-if="mode === 'detail'" :paragraph="paragraphDetail" :disabled="disabled" :loading="busy" @edit="handleEdit" />
        <div v-else class="flex-column min-h-0 min-w-0 flex-1">
          <ParagraphForm ref="paragraphFormRef" v-model="paragraphForm" :knowledge-id="targetKnowledgeId" :disabled="disabled" />
          <div class="mt-4 flex justify-end gap-3">
            <!-- 取消编辑并返回分段详情 -->
            <el-button :disabled="busy" @click="handleCancelEdit">取消</el-button>
            <!-- 保存分段标题和内容 -->
            <el-button type="primary" :loading="saving" :disabled="disabled || questionLoading || questionAdding" @click="handleSubmit">
              保存
            </el-button>
          </div>
        </div>
        <ParagraphQuestions
          v-model="relatedQuestions"
          v-model:adding="questionAdding"
          v-model:loading="questionLoading"
          :api="api"
          :knowledge-id="targetKnowledgeId"
          :document-id="targetDocumentId"
          :paragraph-id="targetParagraphId"
          :disabled="disabled"
          :blocked="detailLoading || saving"
        />
      </div>
    </div>
  </MkDialog>
</template>
