<script setup lang="ts">
import { useTemplateRef } from 'vue'
import BatchSetUserRoleDialog from './BatchSetUserRoleDialog.vue'

const props = defineProps<{ userIds: string[] }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof BatchSetUserRoleDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.userIds)
}
</script>

<template>
  <el-button type="primary" plain @click="handleOpenDialog">设置角色</el-button>
  <BatchSetUserRoleDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
