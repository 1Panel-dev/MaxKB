<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { KnowledgeWorkflowApi, WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import PublishHistoryDrawer from '@/views/workflow/components/publish-history/PublishHistoryDrawer.vue'
import { MsgSuccess } from '@/utils/message'
import { isSystemResource, isSystemSharedResource, isWorkspaceSharedResource } from '@/utils/resource-context'
import perm from '@/permission/index.ts'

defineOptions({ name: 'ButtonKnowledgePublishHistory' })

const { t } = useI18n({ useScope: 'global' })

const canEdit = computed(() => {
  if (isSystemResource()) return Boolean(perm.knowledge.system.workflowEdit())
  if (isSystemSharedResource()) return Boolean(perm.knowledge.share.workflowEdit())
  if (isWorkspaceSharedResource()) return false
  return Boolean(perm.knowledge.workspace.workflowEdit(props.knowledgeId))
})

const props = defineProps<{ label: string; api: KnowledgeWorkflowApi; knowledgeId: string; selectedId?: string; disabled?: boolean }>()
const visible = defineModel<boolean>('visible', { default: false })
const emit = defineEmits<{
  open: []
  preview: [version: WorkflowVersion]
  restore: [version: WorkflowVersion]
}>()

/* 知识库发布历史查询 */
const versions = ref<WorkflowVersion[]>([])
const loading = ref(false)

function handleOpen() {
  if (props.disabled || loading.value) return
  visible.value = true
  emit('open')
  versions.value = []
  loading.value = true
  return loadWorkflowVersions().finally(() => {
    loading.value = false
  })
}

function loadWorkflowVersions() {
  return props.api.getWorkflowVersions(props.knowledgeId).then((result) => {
    versions.value = result
  })
}

/* 版本编辑：成功后重新查询列表，保存失败保留弹窗草稿。 */
const publishHistoryDrawerRef = useTemplateRef<InstanceType<typeof PublishHistoryDrawer>>('publishHistoryDrawerRef')

function handleSubmit(payload: WorkflowVersionPayload, versionId: string) {
  if (loading.value || !versionId) return
  loading.value = true
  return props.api
    .putWorkflowVersion(props.knowledgeId, versionId, payload)
    .then(() => {
      publishHistoryDrawerRef.value?.closeEdit()
      MsgSuccess(t('common.messages.updateSuccess'))
      return loadWorkflowVersions()
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 打开知识库发布历史 -->
  <MkDropdownItem @click="handleOpen">
    <template #icon><MkIcon name="icon_history_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <!-- 发布历史抽屉：由 MkDrawer 按需渲染内容。 -->
  <PublishHistoryDrawer
    ref="publishHistoryDrawerRef"
    v-model="visible"
    :versions="versions"
    :loading="loading"
    :saving="loading"
    :selected-id="selectedId"
    @preview="emit('preview', $event)"
    @restore="emit('restore', $event)"
    @submit="handleSubmit"
    :can-edit="canEdit"
  />
</template>
