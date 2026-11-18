<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationStoreTemplate } from '@/api/types'
import StoreApi from '@/api/admin/store'
import TemplateStoreDialog from '@/views/workflow/components/template-store/TemplateStoreDialog.vue'
import AdvancedCreateDialog from '../create-application/AdvancedCreateDialog.vue'

defineOptions({ name: 'ButtonTemplateStore' })

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ folderId: string }>()
const templateStoreDialogRef = useTemplateRef<InstanceType<typeof TemplateStoreDialog>>('templateStoreDialogRef')
const targetFolderId = ref('default')
const createDialogMounted = ref(false)
const createDialogRef = useTemplateRef<InstanceType<typeof AdvancedCreateDialog>>('createDialogRef')

const templates = ref<ApplicationStoreTemplate[]>([])
const loading = ref(false)

function loadTemplates(keyword: string) {
  loading.value = true
  templates.value = []
  return StoreApi.getStoreApplicationList(keyword ? { name: keyword } : undefined)
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

function handleUse(template: ApplicationStoreTemplate) {
  if (createDialogMounted.value) return
  createDialogMounted.value = true
  nextTick(() => createDialogRef.value?.open(template))
}
</script>

<template>
  <!-- 打开模板中心 -->
  <el-button plain @click="handleOpen">
    <MkIcon name="icon_template_outlined" />
    <span>{{ t('resource.templateStore.title') }}</span>
  </el-button>
  <TemplateStoreDialog
    ref="templateStoreDialogRef"
    resource="application"
    :templates="templates"
    :loading="loading"
    @search="loadTemplates"
    @use="handleUse"
  />
  <AdvancedCreateDialog v-if="createDialogMounted" ref="createDialogRef" :folder-id="targetFolderId" @closed="createDialogMounted = false" />
</template>
