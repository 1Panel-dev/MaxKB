<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import type { SelectInstance } from 'element-plus'
import { useDocumentDetailContext } from '@/views/document-detail/context'
import type { ParagraphProblem } from '@/api/types'
import type { ParagraphQuestionDraft } from '../types'
import { isWorkspaceSharedResource } from '@/utils/resource-context'
import { MsgWarning } from '@/utils/message'

defineOptions({ name: 'ParagraphQuestions' })
const props = defineProps<{
  knowledgeId: string
  documentId: string
  paragraphId?: string
  readonly?: boolean
}>()
const { resourceApi } = useDocumentDetailContext()
const relatedProblems = defineModel<ParagraphQuestionDraft[]>({ required: true })
const loading = ref(false)
const problemAdding = ref(false)
const problemSelectRef = ref<SelectInstance>()
const problemValue = ref('')
const problemOptions = ref<ParagraphProblem[]>([])
const optionLoading = ref(false)

function loadProblemOptions(query = '') {
  optionLoading.value = true
  return resourceApi.problem
    .getProblemsPage(props.knowledgeId, { currentPage: 1, pageSize: 100 }, query.trim() ? { content: query.trim() } : undefined)
    .then(({ records }) => {
      problemOptions.value = records
    })
    .catch(() => {})
    .finally(() => {
      optionLoading.value = false
    })
}

onMounted(() => {
  if (!props.readonly && !isWorkspaceSharedResource()) void loadProblemOptions()
})

/* 新增分段维护本地草稿；已有分段创建或关联问题后刷新关联列表。 */
function refreshRelatedProblems() {
  if (!props.paragraphId) return Promise.resolve()
  return (
    resourceApi.paragraph.getParagraphProblems?.(props.knowledgeId, props.documentId, props.paragraphId).then((problems) => {
      relatedProblems.value = problems
    }) ?? Promise.resolve()
  )
}

async function handleAddProblem() {
  if (props.readonly || loading.value || isWorkspaceSharedResource()) return
  problemAdding.value = true
  await nextTick()
  problemSelectRef.value?.focus()
}

function handleCancelProblem() {
  if (loading.value) return
  problemAdding.value = false
  problemValue.value = ''
}

function handleSelectProblem(value: string) {
  if (props.readonly || loading.value || isWorkspaceSharedResource()) return
  const existingProblem = problemOptions.value.find(({ id }) => id === value)
  const content = (existingProblem?.content ?? value).trim()
  if (!content || content.length > 256) {
    MsgWarning(content ? '问题最多 256 字符' : '请输入关联问题')
    problemValue.value = ''
    return
  }
  if (relatedProblems.value.some((problem) => problem.content.trim() === content)) {
    handleCancelProblem()
    return
  }
  if (!props.paragraphId) {
    relatedProblems.value = [...relatedProblems.value, { content }]
    handleCancelProblem()
    return
  }

  loading.value = true
  const associationRequest = existingProblem
    ? resourceApi.paragraph.putAssociateParagraphProblem?.(props.knowledgeId, props.documentId, props.paragraphId, existingProblem.id)
    : resourceApi.paragraph.postParagraphProblem?.(props.knowledgeId, props.documentId, props.paragraphId, content)
  return (
    associationRequest
      ?.then(() => {
        return refreshRelatedProblems().then(() => {
          problemAdding.value = false
          problemValue.value = ''
        })
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}

function handleRemoveProblem(index: number) {
  if (props.readonly || loading.value || isWorkspaceSharedResource()) return
  const problem = relatedProblems.value[index]
  if (!problem) return
  if (!props.paragraphId) {
    relatedProblems.value = relatedProblems.value.filter((_problem, problemIndex) => problemIndex !== index)
    return
  }
  if (!problem.id) return
  loading.value = true
  void (
    resourceApi.paragraph
      .putUnassociateParagraphProblem?.(props.knowledgeId, props.documentId, props.paragraphId, problem.id)
      .then(() => refreshRelatedProblems())
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <aside v-loading="loading" class="mk-gray-card-lg flex-column w-60 shrink-0">
    <div class="mb-4 flex-between shrink-0 gap-3">
      <h4>关联问题</h4>
      <!-- 添加关联问题 -->
      <el-button v-if="!props.readonly && !isWorkspaceSharedResource()" text :disabled="loading || problemAdding" @click="handleAddProblem">
        <MkIcon name="icon_add_outlined" :size="16" />
      </el-button>
    </div>
    <div class="relative min-h-0 flex-1">
      <el-scrollbar class="absolute! inset-0">
        <div class="space-y-2">
          <!-- 搜索已有问题或输入新问题后添加 -->
          <el-select
            v-if="problemAdding"
            ref="problemSelectRef"
            v-model="problemValue"
            filterable
            allow-create
            default-first-option
            :reserve-keyword="false"
            remote
            :remote-method="loadProblemOptions"
            :loading="optionLoading"
            placeholder="请输入"
            @change="handleSelectProblem"
            @blur="handleCancelProblem"
          >
            <el-option v-for="problem in problemOptions" :key="problem.id" :label="problem.content" :value="problem.id">
              <span class="block truncate" :title="problem.content">{{ problem.content }}</span>
            </el-option>
          </el-select>
          <template v-for="(problem, index) in relatedProblems" :key="problem.content">
            <el-card shadow="never" class="small bg-transparent!" body-class="py-[4px]!">
              <div class="flex-between gap-2">
                <span class="min-w-0 flex-1 truncate" :title="problem.content">{{ problem.content }}</span>
                <!-- 解除问题关联 -->
                <el-button v-if="!props.readonly && !isWorkspaceSharedResource()" text :disabled="loading" @click="handleRemoveProblem(index)">
                  <MkIcon name="icon_close_outlined" :size="16" />
                </el-button>
              </div>
            </el-card>
          </template>
        </div>
      </el-scrollbar>
    </div>
  </aside>
</template>
