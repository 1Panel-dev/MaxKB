<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { SystemUser } from '@/api/types'
import UserPwdDialog from './UserPwdDialog.vue'

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ user: SystemUser }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof UserPwdDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.user)
}
</script>

<template>
  <!-- 修改用户密码 -->
  <MkTooltip :content="t('user.password.changeTitle')" placement="top">
    <el-button type="primary" text @click.stop="handleOpenDialog">
      <MkIcon name="icon-key_outlined" />
    </el-button>
  </MkTooltip>
  <UserPwdDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
