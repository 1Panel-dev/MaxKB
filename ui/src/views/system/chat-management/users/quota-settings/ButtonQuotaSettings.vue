<script setup lang="ts">
import { useTemplateRef } from 'vue'
import QuotaSettingsDialog from './QuotaSettingsDialog.vue'

const props = defineProps<{ userIds: string | string[]; dropdown?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof QuotaSettingsDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.userIds)
}
</script>

<template>
  <MkDropdownItem v-if="dropdown" @click="handleOpenDialog">
    <template #icon><MkIcon name="icon_edit_outlined" /></template>
    <span>配额设置</span>
  </MkDropdownItem>
  <el-button v-else type="primary" plain @click="handleOpenDialog">配额设置</el-button>
  <QuotaSettingsDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
