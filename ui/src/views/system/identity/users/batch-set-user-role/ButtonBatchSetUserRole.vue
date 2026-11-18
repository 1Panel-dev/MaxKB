<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import BatchSetUserRoleDialog from './BatchSetUserRoleDialog.vue'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ userIds: string[] }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof BatchSetUserRoleDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.userIds)
}
</script>

<template>
  <!-- 批量设置用户角色 -->
  <el-button type="primary" plain @click="handleOpenDialog">{{ t('system.user.role.set') }}</el-button>
  <BatchSetUserRoleDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
