<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import CleanStrategyDialog from './CleanStrategyDialog.vue'

const { t } = useI18n({ useScope: 'global' })

/* 清除策略 */
const dialogRef = useTemplateRef<InstanceType<typeof CleanStrategyDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open()
}
</script>

<template>
  <el-button plain @click="handleOpenDialog">
    <MkIcon name="icon_clear_outlined" />
    <span>{{ t('operateLog.cleanStrategy.title') }}</span>
  </el-button>
  <CleanStrategyDialog ref="dialogRef" />
</template>
