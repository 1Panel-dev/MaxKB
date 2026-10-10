<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { TableInstance, TreeNode } from 'element-plus'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { LarkDocumentNode } from '@/api/types'
import DocumentStrategyForm from '@/views/knowledge/create-knowledge/components/DocumentStrategyForm.vue'
import { getFileIconUrl } from '@/utils/icon'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'LarkImportDocumentDrawer' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; folderToken: string }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()

/* 飞书目录与选择：仅展开时加载，文件夹沿用 v2 导入协议。 */
interface LarkDocumentRow extends LarkDocumentNode {
  hasChildren: boolean
}
const visible = ref(false)
const loading = ref(false)
const pendingLoads = ref(0)
const activeStep = ref(0)
const strategyMounted = ref(false)
const documentRows = ref<LarkDocumentRow[]>([])
const documentTableRef = useTemplateRef<{ tableRef?: TableInstance }>('documentTableRef')
const selectedDocuments = ref<LarkDocumentNode[]>([])
const strategyRef = useTemplateRef<InstanceType<typeof DocumentStrategyForm>>('strategyRef')
const folderRequests = new Map<string, Promise<LarkDocumentRow[]>>()
function selectImportedDocuments(documents: LarkDocumentRow[]) {
  documents.filter((document) => document.is_exist).forEach((document) => documentTableRef.value?.tableRef?.toggleRowSelection(document, true, true))
}
function open() {
  visible.value = true
  void loadFolder(props.folderToken)
    .then((documents) => {
      documentRows.value = documents
      return nextTick(() => selectImportedDocuments(documents))
    })
    .catch(() => {
      /* 请求层提示错误，可通过重新打开抽屉重试。 */
    })
}

/* 懒加载目录：读取全部分页，同一目录请求复用，失败可重试。 */
function loadFolder(token: string): Promise<LarkDocumentRow[]> {
  if (!token) return Promise.resolve([])
  const existingRequest = folderRequests.get(token)
  if (existingRequest) return existingRequest
  pendingLoads.value += 1
  const folderDocuments: LarkDocumentRow[] = []
  function loadPage(pageToken?: string): Promise<void> {
    return props.api.getLarkDocumentList(props.knowledgeId, token, pageToken ? { page_token: pageToken } : {}).then((page) => {
      folderDocuments.push(...page.files.map((document) => ({ ...document, hasChildren: document.type === 'folder' })))
      if (page.has_more && page.next_page_token) return loadPage(page.next_page_token)
    })
  }
  const request = loadPage()
    .then(() => folderDocuments)
    .catch((error: unknown) => {
      folderRequests.delete(token)
      throw error
    })
    .finally(() => {
      pendingLoads.value -= 1
    })
  folderRequests.set(token, request)
  return request
}
function loadNode(document: LarkDocumentRow, treeNode: TreeNode, resolve: (documents: LarkDocumentRow[]) => void) {
  void loadFolder(document.token)
    .then((documents) => {
      resolve(documents)
      return nextTick(() => selectImportedDocuments(documents))
    })
    .catch(() => {
      /* Table 无 reject 回调，恢复加载标记以便再次展开重试。 */
      treeNode.loading = false
    })
}

/* 处理策略与正式导入 */
function handleNext() {
  if (loading.value || pendingLoads.value) return
  selectedDocuments.value = ((documentTableRef.value?.tableRef?.getSelectionRows() ?? []) as LarkDocumentNode[]).filter(
    (document) => !document.is_exist,
  )
  if (!selectedDocuments.value.length) {
    MsgWarning('请选择文档')
    return
  }
  strategyMounted.value = true
  activeStep.value = 1
}
function handleSubmit() {
  if (loading.value || !strategyRef.value) return
  loading.value = true
  return strategyRef.value
    .validate()
    .then((valid) => {
      if (!valid || !strategyRef.value) return
      const strategy = strategyRef.value.getStrategy()
      return props.api
        .postImportLarkDocuments(
          props.knowledgeId,
          selectedDocuments.value.map(({ name, token, type }) => ({
            name,
            token,
            type,
            doc_strategy: strategy,
          })),
        )
        .then(() => {
          MsgSuccess('导入成功')
          visible.value = false
          emit('refresh')
        })
    })
    .catch(() => {
      /* 请求层统一提示错误，保留选择与策略。 */
    })
    .finally(() => {
      loading.value = false
    })
}
defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" direction="btt" @closed="emit('closed')">
    <template #header>
      <div class="flex w-full">
        <h4>导入文档</h4>
        <el-steps :active="activeStep" finish-status="success" class="absolute-center w-85!">
          <el-step title="导入文档" />
          <el-step title="文档处理策略" />
        </el-steps>
      </div>
    </template>
    <div v-loading="loading" class="mx-auto w-full max-w-200">
      <section v-show="activeStep === 0">
        <h4 class="mb-4 mk-title-decoration">导入文档</h4>
        <el-alert type="primary" show-icon :closable="false" class="mb-4!">
          <template #icon><MkIcon name="icon_info_filled" /></template>
          <ol class="list-inside list-decimal space-y-1">
            <li>支持文档和表格类型，包含 TXT、Markdown、PDF、DOCX、HTML、XLS、XLSX、CSV、ZIP 格式</li>
            <li>导入文档前，建议规范文档的分段标识。</li>
          </ol>
        </el-alert>

        <MkTable
          ref="documentTableRef"
          v-loading="pendingLoads > 0"
          :data="documentRows"
          row-key="token"
          :load="loadNode"
          :max-table-height="430"
          lazy
        >
          <!-- 选择文档或文件夹，全选由表格维护 -->
          <el-table-column type="selection" width="40" reserve-selection :selectable="(row: LarkDocumentRow) => !row.is_exist" />
          <el-table-column class-name="expand-name-column" label="全部文档" prop="name">
            <template #default="{ row }: { row: LarkDocumentRow }">
              <div class="flex-align-center min-w-0 flex-1 gap-2">
                <img v-if="row.type === 'folder'" src="@/assets/file-type/file-icon.svg" alt="" class="w-4.5 shrink-0" />
                <img
                  v-else
                  :src="getFileIconUrl(row.type === 'docx' ? `${row.name}.docx` : row.type === 'sheet' ? `${row.name}.xlsx` : row.name)"
                  alt=""
                  class="w-4.5 shrink-0"
                />
                <span :title="row.name" class="min-w-0 truncate">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
        </MkTable>
      </section>
      <section v-if="strategyMounted" v-show="activeStep === 1">
        <h4 class="mb-4 mk-title-decoration">文档处理策略</h4>
        <DocumentStrategyForm ref="strategyRef" />
      </section>
    </div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 返回文档选择 -->
      <el-button plain v-if="activeStep === 1" :disabled="loading" @click="activeStep = 0">上一步</el-button>
      <!-- 进入文档处理策略 -->
      <el-button v-if="activeStep === 0" type="primary" :disabled="!folderToken || pendingLoads > 0" @click="handleNext">下一步</el-button>
      <!-- 提交飞书文档导入 -->
      <el-button v-else type="primary" :loading="loading" @click="handleSubmit">开始导入</el-button>
    </template>
  </MkDrawer>
</template>
