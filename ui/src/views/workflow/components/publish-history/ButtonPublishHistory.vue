<script setup lang="ts">
import type WorkflowVersionApi from '@/api/admin/workspace/application/workflow-version'
import type { WorkflowVersion } from '@/api/types'
import PublishHistory from './PublishHistory.vue'

defineOptions({ name: 'ButtonPublishHistory' })

const props = defineProps<{
  resourceId: string
  api: typeof WorkflowVersionApi
  selectedId?: string
  disabled?: boolean
}>()
const visible = defineModel<boolean>('visible', { default: false })
const emit = defineEmits<{
  open: []
  close: []
  preview: [version: WorkflowVersion]
  restore: [version: WorkflowVersion]
  update: [version: WorkflowVersion]
}>()

function handleOpen() {
  if (props.disabled) return
  visible.value = true
  emit('open')
}

function handleClose() {
  if (props.disabled) return
  visible.value = false
  emit('close')
}
</script>

<template>
  <!-- 打开发布历史 -->
  <MkDropdownItem :disabled="disabled" @click="handleOpen">
    <template #icon><MkIcon name="icon_history_outlined" /></template>
    <span>发布历史</span>
  </MkDropdownItem>
  <!-- 面板脱离下拉菜单定位，关闭菜单后仍保持展示。 -->
  <Teleport to="body">
    <div v-if="visible" class="fixed right-0 bottom-0 z-20 h-layout-content w-80 max-w-full">
      <PublishHistory
        :resource-id="resourceId"
        :api="api"
        :selected-id="selectedId"
        :disabled="disabled"
        @preview="emit('preview', $event)"
        @restore="emit('restore', $event)"
        @update="emit('update', $event)"
        @close="handleClose"
      />
    </div>
  </Teleport>
</template>
