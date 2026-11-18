<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationChatLogApi } from '../../context'
import CleanStrategyDialog from './CleanStrategyDialog.vue'

defineOptions({ name: 'ButtonCleanStrategy' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api: ApplicationChatLogApi; applicationId: string }>()
const dialogRef = useTemplateRef<InstanceType<typeof CleanStrategyDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 设置对话日志清除策略 -->
  <el-button plain @click="handleOpenDialog">
    <MkIcon name="icon_clear_outlined" />
    <span>{{ t('application.chatLog.cleanStrategy.title') }}</span>
  </el-button>
  <CleanStrategyDialog :api="props.api" ref="dialogRef" :application-id="props.applicationId" />
</template>
