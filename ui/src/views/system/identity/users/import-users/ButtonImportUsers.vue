<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import ImportUsersDialog from './ImportUsersDialog.vue'

const { t } = useI18n({ useScope: 'global' })

const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof ImportUsersDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open()
}
</script>

<template>
  <!-- 导入用户 -->
  <el-button plain @click="handleOpenDialog">
    <MkIcon name="icon_import_outlined" />
    <span>{{ t('system.user.import.title') }}</span>
  </el-button>
  <ImportUsersDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
