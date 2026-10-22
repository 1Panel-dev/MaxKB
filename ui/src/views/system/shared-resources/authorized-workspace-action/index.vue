<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type { SharedResourceType } from '@/api/types'
import AuthorizedWorkspaceDialog from './AuthorizedWorkspaceDialog.vue'

defineOptions({ name: 'AuthorizedWorkspaceAction' })
const props = defineProps<{
  resource: { id: string }
  resourceType: SharedResourceType
  label: string
}>()

/* 打开工作空间授权弹窗。 */
const authorizedWorkspaceDialogRef = useTemplateRef<InstanceType<typeof AuthorizedWorkspaceDialog>>('authorizedWorkspaceDialogRef')
function handleOpenAuthorizedWorkspace() {
  return authorizedWorkspaceDialogRef.value?.open(props.resource, props.resourceType)
}
</script>

<template>
  <!-- 授权工作空间 -->
  <MkDropdownItem @click.stop="handleOpenAuthorizedWorkspace">
    <template #icon><MkIcon name="icon-lock" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <AuthorizedWorkspaceDialog ref="authorizedWorkspaceDialogRef" />
</template>
