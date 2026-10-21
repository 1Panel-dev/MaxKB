<script setup lang="ts">
import { useTemplateRef } from 'vue'
import AccessRestrictionDialog from './AccessRestrictionDialog.vue'

defineOptions({ name: 'ButtonAccessRestriction' })

const dialogRef = useTemplateRef<InstanceType<typeof AccessRestrictionDialog>>('dialogRef')

function handleOpenAccessRestriction() {
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 设置访问限制 -->
  <el-button plain @click="handleOpenAccessRestriction">
    <MkIcon name="icon-lock" />
    <span>访问限制</span>
  </el-button>
  <AccessRestrictionDialog ref="dialogRef" />
</template>
