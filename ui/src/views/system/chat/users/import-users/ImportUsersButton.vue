<script setup lang="ts">
import { useTemplateRef } from 'vue'
import ImportUsersDialog from './ImportUsersDialog.vue'

const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof ImportUsersDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open()
}
</script>

<template>
  <el-button plain class="ml-3" @click="handleOpenDialog">
    <MkIcon name="icon_import_outlined" />
    <span>导入用户</span>
  </el-button>
  <ImportUsersDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
