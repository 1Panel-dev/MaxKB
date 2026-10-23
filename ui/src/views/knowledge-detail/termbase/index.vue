<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type MkQuickCreate from '@/components/global/mk-table/MkQuickCreate.vue'
import type { ResourceDetailPageProps } from '@/layout/ResourceDetailLayout.vue'
import type { TermbaseItem } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { MsgSuccess } from '@/utils/message'
import { isWorkspaceSharedResource } from '@/utils/resource-context'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import ButtonCreateTermbase from './components/ButtonCreateTermbase.vue'

defineOptions({ name: 'TermbaseView' })
defineProps<ResourceDetailPageProps>()
defineExpose({ customHeader: true })

const route = useRoute()
const knowledgeId = computed(() => String(route.params.knowledgeId ?? ''))
const { resourceApi } = useKnowledgeDetailContext()
const loading = ref(false)
const operationLoading = ref(false)
const termbases = ref<TermbaseItem[]>([])
const searchText = ref('')
const paginationConfig = ref({ currentPage: 1, pageSize: 20, total: 0 })
const selectedTermbases = ref<TermbaseItem[]>([])
const termbaseTableRef = ref<{ clearSelection: () => void }>()
const quickCreateRef = ref<InstanceType<typeof MkQuickCreate>>()

const selectedTermbaseIds = computed(() => selectedTermbases.value.map(({ id }) => id))

function clearSelection() {
  termbaseTableRef.value?.clearSelection()
  selectedTermbases.value = []
}

/* 查询只传服务端支持的内容条件，不在前端重复筛选。 */
function loadTermbases() {
  const { currentPage, pageSize } = paginationConfig.value
  loading.value = true
  return resourceApi.termbase
    .getTermbasePage(knowledgeId.value, { currentPage, pageSize }, { content: searchText.value.trim() || undefined })
    .then(({ records, total }) => {
      termbases.value = records
      paginationConfig.value.total = total
    })
    .catch(() => {
      // 请求层统一提示错误，失败时不以空数据覆盖当前列表。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleSearchChange() {
  paginationConfig.value.currentPage = 1
  clearSelection()
  return loadTermbases()
}

function handleSelectionChange(selection: unknown[]) {
  selectedTermbases.value = selection as TermbaseItem[]
}

function handleTermbasesCreated() {
  paginationConfig.value.currentPage = 1
  clearSelection()
  return loadTermbases()
}

/* 快捷创建与弹窗创建复用同一批量创建接口。 */
function handleQuickCreate(content: string) {
  if (operationLoading.value) return

  operationLoading.value = true
  return (
    resourceApi.termbase.postTermbases?.(knowledgeId.value, [content]).then(() => {
      quickCreateRef.value?.close()
      MsgSuccess('创建成功')
      return handleTermbasesCreated()
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 请求层统一提示错误，失败时保留快捷创建草稿。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function handleDeleteTermbase(termbase: TermbaseItem) {
  if (operationLoading.value) return

  operationLoading.value = true
  return (
    resourceApi.termbase.deleteTermbase?.(knowledgeId.value, termbase.id).then(() => {
      MsgSuccess('删除成功')
      clearSelection()
      return loadTermbases()
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 请求失败时保持当前数据和选择。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function handleBatchDeleteTermbases() {
  const termbaseIds = [...selectedTermbaseIds.value]
  if (operationLoading.value || !termbaseIds.length) return

  operationLoading.value = true
  return (
    resourceApi.termbase.putBatchDeleteTermbases?.(knowledgeId.value, termbaseIds).then(() => {
      MsgSuccess('删除成功')
      clearSelection()
      return loadTermbases()
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 请求失败时保持当前数据和选择。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

function handleExportTermbases() {
  const termbaseIds = [...selectedTermbaseIds.value]
  if (operationLoading.value || !termbaseIds.length) return

  operationLoading.value = true
  return (
    resourceApi.termbase.postExportTermbases?.(knowledgeId.value, termbaseIds).then((content) => {
      const url = URL.createObjectURL(new Blob([content], { type: 'text/plain;charset=utf-8' }))
      const link = document.createElement('a')
      link.href = url
      link.download = 'termbase_export.txt'
      link.click()
      URL.revokeObjectURL(url)
      MsgSuccess('导出成功')
    }) ?? Promise.resolve()
  )
    .catch(() => {
      // 请求层统一提示错误，导出失败时保留选择。
    })
    .finally(() => {
      operationLoading.value = false
    })
}

onMounted(() => {
  void loadTermbases()
})
</script>

<template>
  <Teleport v-if="headerTarget" :to="headerTarget">
    <div class="flex-between gap-4">
      <h4>{{ title }}</h4>
      <div class="flex-align-center gap-3">
        <MkSearchInput v-model="searchText" class="w-60!" @change="handleSearchChange" />
        <ButtonCreateTermbase v-if="!isWorkspaceSharedResource()" :knowledge-id="knowledgeId" @refresh="handleTermbasesCreated" />
      </div>
    </div>
  </Teleport>
  <MkTable
    ref="termbaseTableRef"
    v-model:pagination-config="paginationConfig"
    v-loading="loading || operationLoading"
    :data="termbases"
    @current-change="loadTermbases"
    @size-change="loadTermbases"
    @selection-change="handleSelectionChange"
  >
    <template #body-prepend>
      <!-- 快速创建词语 -->
      <MkQuickCreate
        v-if="!isWorkspaceSharedResource()"
        ref="quickCreateRef"
        text="快速创建词语"
        placeholder="请输入词语"
        :loading="operationLoading"
        @create="handleQuickCreate"
      />
    </template>
    <el-table-column type="selection" width="40" />
    <el-table-column prop="content" label="词语" show-overflow-tooltip />
    <el-table-column prop="create_time" label="创建时间" width="180">
      <template #default="{ row }: { row: TermbaseItem }">
        {{ datetimeFormat(row.create_time) }}
      </template>
    </el-table-column>
    <el-table-column prop="update_time" label="更新时间" width="180">
      <template #default="{ row }: { row: TermbaseItem }">
        {{ datetimeFormat(row.update_time) }}
      </template>
    </el-table-column>
    <el-table-column label="操作" width="64">
      <template #default="{ row }: { row: TermbaseItem }">
        <!-- 删除词语 -->
        <MkTooltip content="删除" placement="top">
          <el-button type="primary" text :disabled="operationLoading" @click="handleDeleteTermbase(row)">
            <MkIcon name="icon_delete-trash_outlined" />
          </el-button>
        </MkTooltip>
      </template>
    </el-table-column>
    <template #footer-batch-actions>
      <!-- 批量导出词语 -->
      <el-button type="primary" plain :disabled="operationLoading" @click="handleExportTermbases">导出</el-button>
      <!-- 批量删除词语 -->
      <el-button v-if="!isWorkspaceSharedResource()" type="danger" plain :loading="operationLoading" @click="handleBatchDeleteTermbases">
        删除
      </el-button>
    </template>
  </MkTable>
</template>
