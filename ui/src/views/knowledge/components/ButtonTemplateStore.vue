<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import StoreApi from '@/api/admin/store'
import type { WorkflowStoreTemplate } from '@/api/types'
import TemplateStoreDialog from '@/views/workflow/components/template-store/TemplateStoreDialog.vue'
import WorkflowKnowledgeDialog from '../create-knowledge/WorkflowKnowledgeDialog.vue'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'ButtonTemplateStore' })
const props = defineProps<{ folderId: string }>()
const templateStoreDialogRef = useTemplateRef<InstanceType<typeof TemplateStoreDialog>>('templateStoreDialogRef')
const emit = defineEmits<{ refresh: [] }>()

/* 模板查询与目标文件夹 */
const targetFolderId = ref('default')
const createDialogMounted = ref(false)
const createDialogRef = useTemplateRef<InstanceType<typeof WorkflowKnowledgeDialog>>('createDialogRef')

const templates = ref<WorkflowStoreTemplate[]>([])
const loading = ref(false)

function loadTemplates(keyword: string) {
  if (loading.value) return
  loading.value = true
  templates.value = []
  return StoreApi.getStoreKnowledgeList(keyword ? { name: keyword } : undefined)
    .then((response) => {
      templates.value = response.apps.map((template) => ({ ...template, desc: template.description ?? template.desc }))
    })
    .finally(() => {
      loading.value = false
    })
}

function handleOpen() {
  targetFolderId.value = props.folderId || 'default'
  templateStoreDialogRef.value?.open()
}

/* 使用模板创建工作流知识库 */
function handleUse(template: WorkflowStoreTemplate) {
  if (createDialogMounted.value) return
  const downloadUrl = template.downloadUrl
  if (!downloadUrl) {
    MsgError('模板缺少下载地址，无法使用')
    return
  }
  createDialogMounted.value = true
  nextTick(() => createDialogRef.value?.open({ ...template, downloadUrl }))
}
function handleCreated() {
  templateStoreDialogRef.value?.close()
  emit('refresh')
}
</script>

<template>
  <!-- 打开模板中心 -->
  <el-button plain @click="handleOpen">
    <MkIcon name="icon_template_outlined" />
    <span>模板中心</span>
  </el-button>
  <TemplateStoreDialog
    ref="templateStoreDialogRef"
    resource="knowledge"
    :templates="templates"
    :loading="loading"
    @search="loadTemplates"
    @use="handleUse"
  />
  <WorkflowKnowledgeDialog
    v-if="createDialogMounted"
    ref="createDialogRef"
    :folder-id="targetFolderId"
    @closed="createDialogMounted = false"
    @refresh="handleCreated"
  />
</template>
