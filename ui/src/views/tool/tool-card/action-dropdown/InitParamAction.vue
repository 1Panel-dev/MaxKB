<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type { ToolItem } from '@/api/types'
import InitParamDrawer from '../InitParamDrawer.vue'

defineOptions({ name: 'InitParamAction' })

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const dialogMounted = ref(false)
const initParamDrawerRef = useTemplateRef<InstanceType<typeof InitParamDrawer>>('initParamDrawerRef')

function handleOpenInitParam() {
  loading.value = true
  return props.api
    .getToolDetail(props.tool.id)
    .then((toolDetail) => {
      dialogMounted.value = true
      return nextTick(() => initParamDrawerRef.value?.open(toolDetail))
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
  <!-- 启动参数 -->
  <MkDropdownItem @click="handleOpenInitParam">
    <template #icon><MkIcon name="icon_preferences_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <InitParamDrawer v-if="dialogMounted" ref="initParamDrawerRef" :api="api" @closed="handleDialogClosed" @update="emit('update', $event)" />
</template>
