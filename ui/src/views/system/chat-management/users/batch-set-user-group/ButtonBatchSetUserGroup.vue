<script setup lang="ts">
import { useTemplateRef } from 'vue'
import BatchSetUserGroupDialog from './BatchSetUserGroupDialog.vue'

const props = defineProps<{ userIds: string[] }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof BatchSetUserGroupDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.userIds)
}
</script>

<template>
  <el-button type="primary" plain @click="handleOpenDialog">设置用户组</el-button>
  <BatchSetUserGroupDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
