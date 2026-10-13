<script setup lang="ts">
import { ref } from 'vue'
import { cloneDeep } from 'lodash'
import ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { DocumentImportParagraph, ParagraphUpdatePayload } from '@/api/types'
import type { ParagraphQuestionDraft } from '@/views/knowledge-detail/paragraph/paragraph-dialog/types'
import ParagraphForm from '@/views/knowledge-detail/paragraph/paragraph-dialog/components/ParagraphForm.vue'
import ParagraphQuestions from '@/views/knowledge-detail/paragraph/paragraph-dialog/components/ParagraphQuestions.vue'

defineOptions({ name: 'EditImportParagraphDialog' })
defineProps<{ knowledgeId: string }>()
const emit = defineEmits<{ submit: [paragraph: DocumentImportParagraph]; closed: [] }>()

/* 编辑弹窗按需挂载，保存前仅维护导入分段和关联问题的本地草稿。 */
const visible = ref(false)
const paragraphDraft = ref<DocumentImportParagraph>({ title: '', content: '' })
const paragraphForm = ref<ParagraphUpdatePayload>({ title: '', content: '' })
const paragraphFormRef = ref<InstanceType<typeof ParagraphForm>>()
const relatedQuestions = ref<ParagraphQuestionDraft[]>([])
const loading = ref(false)

function open(paragraph: DocumentImportParagraph) {
  paragraphDraft.value = cloneDeep(paragraph)
  paragraphForm.value = { title: paragraph.title ?? '', content: paragraph.content }
  relatedQuestions.value = cloneDeep(paragraph.problem_list ?? [])
  visible.value = true
}

function close() {
  if (!loading.value) visible.value = false
}

function handleBeforeClose(done: () => void) {
  if (!loading.value) done()
}

function handleSubmit() {
  if (loading.value) return
  loading.value = true
  void paragraphFormRef.value
    ?.validate()
    .then((valid) => {
      if (!valid) return
      emit('submit', {
        ...paragraphDraft.value,
        title: paragraphForm.value.title.trim(),
        content: paragraphForm.value.content,
        problem_list: relatedQuestions.value.map(({ content }) => ({ content })),
      })
      visible.value = false
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog
    v-model="visible"
    title="编辑"
    width="1000"
    align-center
    content-class="max-h-[calc(100vh-300px)]!"
    :before-close="handleBeforeClose"
    @closed="emit('closed')"
  >
    <div v-loading="loading" class="flex w-full gap-4">
      <ParagraphForm ref="paragraphFormRef" v-model="paragraphForm" :knowledge-id="knowledgeId" />
      <!-- 关联问题仅保存到导入草稿，未创建文档不传入分段 ID -->
      <ParagraphQuestions v-model="relatedQuestions" :api="ParagraphApi" :knowledge-id="knowledgeId" document-id="" />
    </div>
    <template #footer>
      <!-- 取消分段编辑 -->
      <el-button plain :disabled="loading" @click="close">取消</el-button>
      <!-- 保存预览分段及关联问题 -->
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDialog>
</template>
