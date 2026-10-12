<script setup lang="ts">
import { computed, ref } from 'vue'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { ParagraphUpdatePayload } from '@/api/types'
import type { ParagraphQuestionDraft } from './types'
import ParagraphForm from './components/ParagraphForm.vue'
import ParagraphQuestions from './components/ParagraphQuestions.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateParagraphDialog' })
const props = withDefaults(
  defineProps<{
    api: typeof ParagraphApi
    knowledgeId: string
    documentId: string
    disabled?: boolean
  }>(),
  { disabled: false },
)
const emit = defineEmits<{ success: [mode: 'create']; closed: [] }>()

/* 添加弹窗按需挂载，草稿在关闭后随实例释放。 */
const visible = ref(false)
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const paragraphFormRef = ref<InstanceType<typeof ParagraphForm>>()
const paragraphForm = ref<ParagraphUpdatePayload>({ title: '', content: '' })
const relatedQuestions = ref<ParagraphQuestionDraft[]>([])
const questionAdding = ref(false)
const questionLoading = ref(false)
const saving = ref(false)
const busy = computed(() => saving.value || questionLoading.value)

function open() {
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.documentId
  visible.value = true
}

function close() {
  if (!busy.value) visible.value = false
}

function handleBeforeClose(done: () => void) {
  if (!busy.value) done()
}

function handleSubmit() {
  if (props.disabled || busy.value || questionAdding.value) return
  void paragraphFormRef.value
    ?.validate()
    .then((valid) => {
      if (!valid || props.disabled || busy.value || questionAdding.value) return
      saving.value = true
      return props.api
        .postParagraph(targetKnowledgeId.value, targetDocumentId.value, {
          title: paragraphForm.value.title.trim(),
          content: paragraphForm.value.content,
          is_active: true,
          problem_list: relatedQuestions.value.map(({ content }) => ({ content })),
        })
        .then(() => {
          visible.value = false
          MsgSuccess('添加成功')
          emit('success', 'create')
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
  <MkDialog v-model="visible" title="添加分段" width="1000" align-center :before-close="handleBeforeClose" @closed="emit('closed')">
    <div v-loading="saving" class="flex w-full gap-4">
      <ParagraphForm ref="paragraphFormRef" v-model="paragraphForm" :knowledge-id="targetKnowledgeId" :disabled="disabled" />
      <ParagraphQuestions
        v-model="relatedQuestions"
        v-model:adding="questionAdding"
        v-model:loading="questionLoading"
        :api="api"
        :knowledge-id="targetKnowledgeId"
        :document-id="targetDocumentId"
        :disabled="disabled"
        :blocked="saving"
      />
    </div>
    <template #footer>
      <!-- 取消添加分段 -->
      <el-button plain :disabled="busy" @click="close">取消</el-button>
      <!-- 提交新增分段和关联问题 -->
      <el-button type="primary" :loading="saving" :disabled="disabled || questionAdding" @click="handleSubmit">添加</el-button>
    </template>
  </MkDialog>
</template>
