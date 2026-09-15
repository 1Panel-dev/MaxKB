<script setup lang="ts">
import { useTemplateRef } from 'vue'
import CleanStrategyDialog from './CleanStrategyDialog.vue'

/* 清除策略 */
const dialogRef = useTemplateRef<InstanceType<typeof CleanStrategyDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open()
}
</script>

<template>
  <el-button plain @click="handleOpenDialog">
    <MkIcon name="icon_clear_outlined" />
    <span>清除策略</span>
  </el-button>
  <CleanStrategyDialog ref="dialogRef" />
</template>
