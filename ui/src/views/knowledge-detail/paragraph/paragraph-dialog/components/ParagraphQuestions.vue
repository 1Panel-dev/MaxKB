<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { Plus, Close } from '@element-plus/icons-vue'
import type { FormInstance, FormRules, InputInstance } from 'element-plus'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { ParagraphQuestionDraft } from '../types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ParagraphQuestions' })
const props = withDefaults(
  defineProps<{
    api: typeof ParagraphApi
    knowledgeId: string
    documentId: string
    paragraphId?: string
    disabled?: boolean
    blocked?: boolean
  }>(),
  { disabled: false, blocked: false },
)
const relatedProblems = defineModel<ParagraphQuestionDraft[]>({ required: true })
const problemSaving = defineModel<boolean>('loading', { default: false })
const problemAdding = defineModel<boolean>('adding', { default: false })
const problemFormRef = ref<FormInstance>()
const problemInputRef = ref<InputInstance>()
const problemForm = ref({ content: '' })
const busy = computed(() => props.disabled || props.blocked || problemSaving.value)

/* 新增分段使用本地问题草稿；已有分段通过专属接口即时保存。 */
async function handleAddProblem() {
  if (busy.value) return
  problemAdding.value = true
  await nextTick()
  problemInputRef.value?.focus()
}

function handleCancelProblem() {
  if (busy.value) return
  problemAdding.value = false
  problemForm.value.content = ''
  problemFormRef.value?.clearValidate()
}

function handleSubmitProblem() {
  if (busy.value) return
  void problemFormRef.value
    ?.validate()
    .then(() => {
      if (busy.value) return
      const content = problemForm.value.content.trim()
      if (!props.paragraphId) {
        relatedProblems.value = [...relatedProblems.value, { content }]
        handleCancelProblem()
        return
      }
      problemSaving.value = true
      return props.api
        .postParagraphProblem(props.knowledgeId, props.documentId, props.paragraphId, content)
        .then((problem) => {
          relatedProblems.value = [...relatedProblems.value, problem]
          problemAdding.value = false
          problemForm.value.content = ''
          MsgSuccess('关联成功')
        })
        .finally(() => {
          problemSaving.value = false
        })
    })
    .catch(() => {})
}

function handleRemoveProblem(index: number) {
  if (busy.value) return
  const problem = relatedProblems.value[index]
  if (!problem) return
  if (!props.paragraphId) {
    relatedProblems.value = relatedProblems.value.filter((_problem, problemIndex) => problemIndex !== index)
    return
  }
  if (!problem.id) return
  problemSaving.value = true
  void props.api
    .putUnassociateParagraphProblem(props.knowledgeId, props.documentId, props.paragraphId, problem.id)
    .then(() => {
      relatedProblems.value = relatedProblems.value.filter((_problem, problemIndex) => problemIndex !== index)
    })
    .catch(() => {})
    .finally(() => {
      problemSaving.value = false
    })
}
</script>

<template>
  <aside v-loading="problemSaving" class="mk-gray-card-lg w-60 shrink-0">
    <div class="mb-4 flex-between shrink-0 gap-3">
      <h4>关联问题</h4>
      <!-- 添加关联问题 -->
      <el-button text v-if="!disabled" :disabled="blocked || problemSaving || problemAdding" @click="handleAddProblem">
        <MkIcon name="icon_add_outlined" :size="16" />
      </el-button>
    </div>
    <el-scrollbar class="min-h-0 flex-1">
      <div class="space-y-2">
        <template v-for="(problem, index) in relatedProblems" :key="problem.content">
          <div class="flex-between gap-2 rounded-md border px-3 py-1">
            <span class="min-w-0 break-words">{{ problem.content }}</span>
            <!-- 移除当前分段的关联问题 -->
            <el-button
              text
              circle
              class="shrink-0"
              title="移除关联问题"
              v-if="!disabled"
              :disabled="blocked || problemSaving"
              @click="handleRemoveProblem(index)"
            >
              <MkIcon name="icon_close_outlined" :size="18" />
            </el-button>
          </div>
        </template>
      </div>
    </el-scrollbar>
  </aside>
</template>
