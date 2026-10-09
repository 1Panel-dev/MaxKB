<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type { ElTree, LoadFunction } from 'element-plus'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { KnowledgeDetail, LarkDocumentNode } from '@/api/types'
import DocumentStrategyForm from '@/views/knowledge/create-knowledge/components/DocumentStrategyForm.vue'
import { getFileIconUrl } from '@/utils/icon'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'LarkImportDocumentDrawer' })
const props = defineProps<{ api: typeof DocumentApi; knowledge: KnowledgeDetail }>()
const emit = defineEmits<{ refresh: []; closed: [] }>()

/* 飞书文件树与选择状态：只导入未导入的文件，文件夹用于导航。 */
const visible = ref(false)
const loading = ref(false)
const pendingLoads = ref(0)
const activeStep = ref(0)
const strategyMounted = ref(false)
const loadedNodes = ref<LarkDocumentNode[]>([])
const checkedTokens = ref<string[]>([])
const selectedDocuments = ref<LarkDocumentNode[]>([])
const treeRef = useTemplateRef<InstanceType<typeof ElTree>>('treeRef')
const strategyRef = useTemplateRef<InstanceType<typeof DocumentStrategyForm>>('strategyRef')
const folderToken = computed(() => String(props.knowledge.meta?.folder_token ?? ''))
const selectableNodes = computed(() => loadedNodes.value.filter((node) => !node.is_exist))
const allChecked = computed(() => selectableNodes.value.length > 0 && selectableNodes.value.every((node) => checkedTokens.value.includes(node.token)))
const indeterminate = computed(() => !allChecked.value && selectableNodes.value.some((node) => checkedTokens.value.includes(node.token)))
const treeProps = {
  label: 'name',
  isLeaf: (node: LarkDocumentNode) => node.type !== 'folder',
  disabled: (node: LarkDocumentNode) => node.is_exist,
}
function open() {
  visible.value = true
}
function handleCheck() {
  checkedTokens.value = (treeRef.value?.getCheckedKeys() ?? []).map(String)
}
function handleAllCheck(checked: unknown) {
  const tokens = loadedNodes.value.filter((node) => node.is_exist || Boolean(checked)).map((node) => node.token)
  treeRef.value?.setCheckedKeys(tokens)
  handleCheck()
}

/* 懒加载目录：一次读完该目录分页，失败恢复可重试状态。 */
const loadNode: LoadFunction = (node, resolve, reject) => {
  const token = node.level === 0 ? folderToken.value : String(node.data.token)
  if (!token) {
    resolve([])
    return
  }
  pendingLoads.value += 1
  const folderDocuments: LarkDocumentNode[] = []
  function loadPage(pageToken?: string): Promise<void> {
    return props.api.getLarkDocumentList(props.knowledge.id, token, pageToken ? { page_token: pageToken } : {}).then((page) => {
      folderDocuments.push(...page.files)
      if (page.has_more && page.next_page_token) return loadPage(page.next_page_token)
    })
  }
  void loadPage()
    .then(() => {
      const selectLoaded = allChecked.value
      loadedNodes.value.push(...folderDocuments)
      resolve(folderDocuments)
      return nextTick(() => {
        folderDocuments.forEach((document) => {
          if (document.is_exist || selectLoaded) treeRef.value?.setChecked(document.token, true, false)
        })
        handleCheck()
      })
    })
    .catch(() => {
      reject?.()
    })
    .finally(() => {
      pendingLoads.value -= 1
    })
}

/* 处理策略与正式导入 */
function handleNext() {
  if (loading.value || pendingLoads.value) return
  selectedDocuments.value = ((treeRef.value?.getCheckedNodes(true) ?? []) as LarkDocumentNode[]).filter(
    (node) => node.type !== 'folder' && !node.is_exist,
  )
  if (!selectedDocuments.value.length) {
    MsgWarning('请选择需要导入的文档')
    return
  }
  strategyMounted.value = true
  activeStep.value = 1
}
function handleStrategyMounted() {
  strategyRef.value?.setStrategy(props.knowledge.doc_strategy)
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
          props.knowledge.id,
          selectedDocuments.value.map(({ name, token, type }) => ({
            name,
            token,
            type,
            doc_strategy: strategy,
          })),
        )
        .then(() => {
          MsgSuccess('导入任务提交成功')
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
  <MkDrawer v-model="visible" direction="btt" size="100%" :show-close="!loading" @closed="emit('closed')">
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
        <el-alert v-if="!folderToken" type="warning" title="请先在知识库设置中配置飞书文件夹 Token" :closable="false" />
        <template v-else>
          <div class="mk-gray-card-lg mb-3">
            <el-checkbox :model-value="allChecked" :indeterminate="indeterminate" :disabled="pendingLoads > 0" @change="handleAllCheck">
              全部文档
            </el-checkbox>
          </div>
          <el-tree
            ref="treeRef"
            :props="treeProps"
            :load="loadNode"
            node-key="token"
            lazy
            show-checkbox
            style="--el-tree-node-content-height: 44px"
            @check="handleCheck"
          >
            <template #default="{ data }: { data: LarkDocumentNode }">
              <div class="flex-align-center gap-2 py-2">
                <img v-if="data.type === 'folder'" src="@/assets/file-type/file-icon.svg" alt="" class="size-5" />
                <img
                  v-else
                  :src="getFileIconUrl(data.type === 'docx' ? `${data.name}.docx` : data.type === 'sheet' ? `${data.name}.xlsx` : data.name)"
                  alt=""
                  class="size-5"
                />
                <span :title="data.name" class="truncate">{{ data.name }}</span>
                <span v-if="data.is_exist" class="text-N600 text-sm">已导入</span>
              </div>
            </template>
          </el-tree>
        </template>
      </section>
      <section v-if="strategyMounted" v-show="activeStep === 1">
        <h4 class="mb-4 mk-title-decoration">文档处理策略</h4>
        <DocumentStrategyForm ref="strategyRef" @vue:mounted="handleStrategyMounted" />
      </section>
    </div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <!-- 返回文档选择 -->
      <el-button v-if="activeStep === 1" :disabled="loading" @click="activeStep = 0">上一步</el-button>
      <!-- 进入文档处理策略 -->
      <el-button v-if="activeStep === 0" type="primary" :disabled="!folderToken || pendingLoads > 0" @click="handleNext">下一步</el-button>
      <!-- 提交飞书文档导入 -->
      <el-button v-else type="primary" :loading="loading" @click="handleSubmit">开始导入</el-button>
    </template>
  </MkDrawer>
</template>
