<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import StoreApi from '@/api/admin/store'
import type { WorkflowStoreTemplate } from '@/api/types'
import TemplateStoreDialog from '@/views/workflow/components/template-store/TemplateStoreDialog.vue'

defineOptions({ name: 'ButtonKnowledgeTemplateStore' })
const emit = defineEmits<{ open: []; use: [template: WorkflowStoreTemplate] }>()
const templateStoreDialogRef = useTemplateRef<InstanceType<typeof TemplateStoreDialog>>('templateStoreDialogRef')

const templates = ref<WorkflowStoreTemplate[]>([])
const loading = defineModel<boolean>('loading', { default: false })

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
  if (loading.value) return
  emit('open')
  templateStoreDialogRef.value?.open()
}

function close() {
  templateStoreDialogRef.value?.close()
}

defineExpose({ close })
</script>

<template>
  <!-- 打开模板中心 -->
  <el-button plain :disabled="loading" @click="handleOpen">
    <MkIcon name="icon_template_outlined" />
    <span>模板中心</span>
  </el-button>
  <TemplateStoreDialog
    ref="templateStoreDialogRef"
    resource="knowledge"
    :templates="templates"
    :loading="loading"
    @search="loadTemplates"
    @use="emit('use', $event)"
  />
</template>
