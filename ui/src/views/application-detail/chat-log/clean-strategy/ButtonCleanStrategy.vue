<script setup lang="ts">
import { useTemplateRef } from 'vue'
import CleanStrategyDialog from './CleanStrategyDialog.vue'

defineOptions({ name: 'ButtonCleanStrategy' })

const props = defineProps<{ applicationId: string }>()
const dialogRef = useTemplateRef<InstanceType<typeof CleanStrategyDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 设置对话日志清除策略 -->
  <el-button plain @click="handleOpenDialog">
    <MkIcon name="icon_clear_outlined" />
    <span>清除策略</span>
  </el-button>
  <CleanStrategyDialog ref="dialogRef" :application-id="props.applicationId" />
</template>
