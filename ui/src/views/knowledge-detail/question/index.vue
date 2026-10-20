<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { TableColumnCtx } from 'element-plus'
import type { ProblemItem } from '@/api/types'
import type MkQuickCreate from '@/components/global/mk-table/MkQuickCreate.vue'
import MkEditName from '@/components/mk-edit-name/index.vue'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import { datetimeFormat } from '@/utils/time'
import { numberFormat } from '@/utils/number'
import { MsgSuccess } from '@/utils/message'
import { isWorkspaceSharedResource } from '@/utils/resource-context'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import AssociateParagraphDialog from './components/AssociateParagraphDialog.vue'
import ButtonCreateProblem from './components/ButtonCreateProblem.vue'
import ProblemDetailDrawer from './components/ProblemDetailDrawer.vue'

defineOptions({ name: 'QuestionListView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const { knowledgeId, resourceApi } = useKnowledgeDetailContext()
const loading = ref(false)
const operationLoading = ref(false)
const problems = ref<ProblemItem[]>([])
const searchText = ref('')
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const selectedProblems = ref<ProblemItem[]>([])
const problemTableRef = ref<{ clearSelection: () => void }>()
const quickCreateRef = ref<InstanceType<typeof MkQuickCreate>>()
const associateParagraphDialogRef = ref<InstanceType<typeof AssociateParagraphDialog>>()
const detailProblem = ref<ProblemItem>()
const currentIndex = computed(() => problems.value.findIndex(({ id }) => id === detailProblem.value?.id))
const hasPrevious = computed(() => currentIndex.value > 0 || (currentIndex.value === 0 && paginationConfig.value.currentPage > 1))
const hasNext = computed(
  () =>
    currentIndex.value >= 0 &&
    (currentIndex.value < problems.value.length - 1 ||
      paginationConfig.value.currentPage * paginationConfig.value.pageSize < paginationConfig.value.total),
)

function clearSelection() {
  problemTableRef.value?.clearSelection()
  selectedProblems.value = []
}

function loadProblems(currentPage = paginationConfig.value.currentPage): Promise<ProblemItem[] | undefined> {
  loading.value = true
  return resourceApi.problem
    .getProblemsPage(knowledgeId.value, { currentPage, pageSize: paginationConfig.value.pageSize }, { content: searchText.value.trim() || undefined })
    .then(({ records, total }) => {
      const lastPage = Math.max(1, Math.ceil(total / paginationConfig.value.pageSize))
      if (currentPage > lastPage) return loadProblems(lastPage)
      problems.value = records
      paginationConfig.value.currentPage = currentPage
      paginationConfig.value.total = total
      const currentProblem = records.find(({ id }) => id === detailProblem.value?.id)
      if (currentProblem) detailProblem.value = { ...currentProblem }
      return records
    })
    .catch(() => {
      // 请求层提示错误，失败时保留当前列表。
      return undefined
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange() {
  clearSelection()
  return loadProblems(1)
}

function handleSelectionChange(selection: unknown[]) {
  selectedProblems.value = selection as ProblemItem[]
}

function handleQuickCreate(content: string) {
  if (operationLoading.value) return
  operationLoading.value = true
  return (
    resourceApi.problem.postProblems?.(knowledgeId.value, [content]).then(() => {
      quickCreateRef.value?.close()
      MsgSuccess('创建成功')
      return handleSearchChange()
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 创建失败时保留输入。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function handleSaveProblem(problem: ProblemItem, content: string): Promise<string> {
  operationLoading.value = true
  return (
    resourceApi.problem.putProblem?.(knowledgeId.value, problem.id, content).then(() => {
      MsgSuccess('修改成功')
      void loadProblems()
      return content
    }) ?? Promise.reject(new Error('Problem editing is unavailable'))
  ).finally(() => {
    operationLoading.value = false
  })
}

function handleDeleteProblem(problem: ProblemItem) {
  if (operationLoading.value) return
  operationLoading.value = true
  return (
    resourceApi.problem.deleteProblem?.(knowledgeId.value, problem.id).then(() => {
      MsgSuccess('删除成功')
      clearSelection()
      return loadProblems()
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 删除失败时保留列表。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function handleBatchDeleteProblems() {
  if (operationLoading.value || !selectedProblems.value.length) return
  operationLoading.value = true
  return (
    resourceApi.problem
      .putBatchDeleteProblems?.(
        knowledgeId.value,
        selectedProblems.value.map(({ id }) => id),
      )
      .then(() => {
        MsgSuccess('删除成功')
        clearSelection()
        return loadProblems()
      }) ?? Promise.resolve()
  )
    .catch(() => {
      // 删除失败时保留勾选。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function handleOpenAssociateParagraphs(problemIds: string[]) {
  if (operationLoading.value || !problemIds.length) return
  associateParagraphDialogRef.value?.open(problemIds)
}

function handleAssociateParagraphsSuccess() {
  clearSelection()
  return loadProblems()
}

function handleOpenProblem(problem: ProblemItem, column: TableColumnCtx<ProblemItem> | null) {
  if (isWorkspaceSharedResource() || loading.value || operationLoading.value || column?.type === 'selection') return
  detailProblem.value = { ...problem }
}

async function handleNavigateProblem(direction: -1 | 1) {
  if (loading.value || currentIndex.value < 0) return
  const nextProblem = problems.value[currentIndex.value + direction]
  if (nextProblem) {
    detailProblem.value = { ...nextProblem }
    return
  }
  if (!(direction === -1 ? hasPrevious.value : hasNext.value)) return
  clearSelection()
  const records = await loadProblems(paginationConfig.value.currentPage + direction)
  const adjacentProblem = direction === 1 ? records?.[0] : records?.at(-1)
  if (detailProblem.value && adjacentProblem) detailProblem.value = { ...adjacentProblem }
}

onMounted(() => loadProblems())
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between gap-4">
      <h4>{{ title }}</h4>
      <div class="flex-align-center gap-3">
        <MkSearchInput v-model="searchText" class="w-60!" @change="handleSearchChange" />
        <ButtonCreateProblem v-if="!isWorkspaceSharedResource()" @refresh="handleSearchChange" />
      </div>
    </div>
  </Teleport>
  <MkTable
    ref="problemTableRef"
    v-model:pagination-config="paginationConfig"
    v-loading="loading || operationLoading"
    :data="problems"
    @current-change="loadProblems()"
    @size-change="loadProblems()"
    @selection-change="handleSelectionChange"
    @row-click="handleOpenProblem"
  >
    <template #body-prepend>
      <!-- 快速创建问题 -->
      <MkQuickCreate
        v-if="!isWorkspaceSharedResource()"
        ref="quickCreateRef"
        text="快速创建问题"
        placeholder="请输入问题"
        :loading="operationLoading"
        @create="handleQuickCreate"
      />
    </template>
    <el-table-column v-if="!isWorkspaceSharedResource()" type="selection" width="40" />
    <el-table-column prop="content" label="问题" min-width="280">
      <template #default="{ row }: { row: ProblemItem }">
        <MkEditName
          v-model="row.content"
          :disabled="isWorkspaceSharedResource()"
          :maxlength="256"
          :save="(content) => handleSaveProblem(row, content)"
          :title="row.content"
        />
      </template>
    </el-table-column>
    <el-table-column prop="paragraph_count" label="关联分段数" min-width="120" />
    <el-table-column prop="hit_num" label="召回次数" min-width="100">
      <template #default="{ row }: { row: ProblemItem }">{{ numberFormat(row.hit_num) }}</template>
    </el-table-column>
    <el-table-column prop="last_hit_time" label="最近一次召回时间" min-width="180">
      <template #default="{ row }: { row: ProblemItem }">{{ datetimeFormat(row.last_hit_time) || '-' }}</template>
    </el-table-column>
    <el-table-column prop="create_time" label="创建时间" min-width="180">
      <template #default="{ row }: { row: ProblemItem }">{{ datetimeFormat(row.create_time) }}</template>
    </el-table-column>
    <el-table-column prop="update_time" label="更新时间" min-width="180">
      <template #default="{ row }: { row: ProblemItem }">{{ datetimeFormat(row.update_time) }}</template>
    </el-table-column>
    <el-table-column v-if="!isWorkspaceSharedResource()" label="操作" width="100" fixed="right">
      <template #default="{ row }: { row: ProblemItem }">
        <div @click.stop>
          <!-- 关联当前问题的分段 -->
          <MkTooltip content="关联分段" placement="top">
            <el-button type="primary" text :disabled="operationLoading" @click="handleOpenAssociateParagraphs([row.id])">
              <MkIcon name="icon_link-record_outlined" />
            </el-button>
          </MkTooltip>
          <!-- 直接删除问题 -->
          <MkTooltip content="删除" placement="top">
            <el-button type="primary" text :disabled="operationLoading" @click="handleDeleteProblem(row)">
              <MkIcon name="icon_delete-trash_outlined" />
            </el-button>
          </MkTooltip>
        </div>
      </template>
    </el-table-column>
    <template v-if="!isWorkspaceSharedResource()" #footer-batch-actions>
      <!-- 批量关联所选问题的分段 -->
      <el-button type="primary" plain :disabled="operationLoading" @click="handleOpenAssociateParagraphs(selectedProblems.map(({ id }) => id))">
        关联分段
      </el-button>
      <!-- 直接批量删除问题 -->
      <el-button type="danger" plain :disabled="operationLoading" @click="handleBatchDeleteProblems">删除</el-button>
    </template>
  </MkTable>
  <ProblemDetailDrawer
    v-if="detailProblem"
    v-model="detailProblem"
    :has-previous="hasPrevious"
    :has-next="hasNext"
    @previous="handleNavigateProblem(-1)"
    @next="handleNavigateProblem(1)"
    @refresh="loadProblems()"
    @associate="handleOpenAssociateParagraphs([detailProblem.id])"
    @closed="detailProblem = undefined"
  />
  <AssociateParagraphDialog v-if="!isWorkspaceSharedResource()" ref="associateParagraphDialogRef" @success="handleAssociateParagraphsSuccess" />
</template>
