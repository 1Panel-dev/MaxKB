<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import WorkflowApi from '@/api/admin/workspace/tool/workflow'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import PublishHistoryDrawer from '@/views/workflow/components/publish-history/PublishHistoryDrawer.vue'

defineOptions({ name: 'ButtonToolPublishHistory' })

const props = defineProps<{ api?: typeof WorkflowApi; toolId: string; selectedId?: string; disabled?: boolean }>()
const visible = defineModel<boolean>('visible', { default: false })
const emit = defineEmits<{
  open: []
  preview: [version: WorkflowVersion]
  restore: [version: WorkflowVersion]
}>()

/* 工具发布历史查询 */
const versions = ref<WorkflowVersion[]>([])
const loading = ref(false)

function handleOpen() {
  if (props.disabled || loading.value || saving.value) return
  visible.value = true
  emit('open')
  versions.value = []
  return loadWorkflowVersions()
}

function loadWorkflowVersions() {
  loading.value = true
  return (props.api ?? WorkflowApi)
    .getWorkflowVersions(props.toolId)
    .then((result) => {
      versions.value = result
    })
    .finally(() => {
      loading.value = false
    })
}

/* 版本编辑：成功后重新查询列表，保存失败保留弹窗草稿。 */
const saving = ref(false)
const publishHistoryDrawerRef = useTemplateRef<InstanceType<typeof PublishHistoryDrawer>>('publishHistoryDrawerRef')

function handleSubmit(payload: WorkflowVersionPayload, versionId: string) {
  if (saving.value || !versionId) return
  saving.value = true
  return (props.api ?? WorkflowApi)
    .putWorkflowVersion(props.toolId, versionId, payload)
    .then(() => {
      publishHistoryDrawerRef.value?.closeEdit()
      MsgSuccess('修改成功')
      return loadWorkflowVersions()
    })
    .finally(() => {
      saving.value = false
    })
}
</script>

<template>
  <!-- 打开工具发布历史 -->
  <MkDropdownItem divided @click="handleOpen">
    <template #icon><MkIcon name="icon_history_outlined" /></template>
    <span>发布历史</span>
  </MkDropdownItem>
  <!-- 发布历史抽屉：由 MkDrawer 按需渲染内容。 -->
  <PublishHistoryDrawer
    ref="publishHistoryDrawerRef"
    v-model="visible"
    :versions="versions"
    :loading="loading"
    :saving="saving"
    :selected-id="selectedId"
    @preview="emit('preview', $event)"
    @restore="emit('restore', $event)"
    @submit="handleSubmit"
  />
</template>
