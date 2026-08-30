<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import InitParamDialog from '../InitParamDialog.vue'

defineOptions({ name: 'InitParamAction' })

const props = defineProps<{ api: typeof ToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const dialogMounted = ref(false)
const initParamDialogRef = useTemplateRef<InstanceType<typeof InitParamDialog>>('initParamDialogRef')

function handleOpenInitParam() {
  loading.value = true
  return props.api
    .getToolDetail(props.tool.id)
    .then((toolDetail) => {
      dialogMounted.value = true
      return nextTick(() => initParamDialogRef.value?.open(toolDetail))
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <MkDropdownItem @click="handleOpenInitParam">
    <template #icon><MkIcon name="icon_preferences_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <InitParamDialog v-if="dialogMounted" ref="initParamDialogRef" :api="api" @closed="handleDialogClosed" @update="emit('update', $event)" />
</template>
