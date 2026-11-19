<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import QuotaSettingsDialog from './QuotaSettingsDialog.vue'

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ userIds: string | string[]; dropdown?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof QuotaSettingsDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.userIds)
}
</script>

<template>
  <!-- 配额设置 -->
  <MkDropdownItem v-if="dropdown" @click="handleOpenDialog">
    <template #icon><MkIcon name="icon_edit_outlined" /></template>
    <span>{{ t('chatUser.quota.title') }}</span>
  </MkDropdownItem>
  <!-- 配额设置 -->
  <el-button v-else type="primary" plain @click="handleOpenDialog">{{ t('chatUser.quota.title') }}</el-button>
  <QuotaSettingsDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
