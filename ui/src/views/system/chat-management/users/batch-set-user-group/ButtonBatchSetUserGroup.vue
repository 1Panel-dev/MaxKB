<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import BatchSetUserGroupDialog from './BatchSetUserGroupDialog.vue'

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ userIds: string[] }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof BatchSetUserGroupDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.userIds)
}
</script>

<template>
  <!-- 设置用户组 -->
  <el-button type="primary" plain @click="handleOpenDialog">{{ t('userGroup.set') }}</el-button>
  <BatchSetUserGroupDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
