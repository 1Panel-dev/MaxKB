<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type { SystemUser } from '@/api/types'
import UserPwdDialog from './UserPwdDialog.vue'

const props = defineProps<{ user: SystemUser }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof UserPwdDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.user)
}
</script>

<template>
  <el-tooltip content="修改用户密码" placement="top">
    <el-button type="primary" text @click.stop="handleOpenDialog">
      <MkIcon name="icon-key_outlined" />
    </el-button>
  </el-tooltip>
  <UserPwdDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
