<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ChatUser } from '@/api/types'
import UserPwdDialog from './UserPwdDialog.vue'

const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{ user: ChatUser }>()
const emit = defineEmits<{ refresh: [] }>()

/* 打开弹窗 */
const dialogRef = useTemplateRef<InstanceType<typeof UserPwdDialog>>('dialogRef')

function handleOpenDialog() {
  dialogRef.value?.open(props.user)
}
</script>

<template>
  <MkTooltip :content="t('user.password.changeTitle')" placement="top">
    <!-- 修改用户密码 -->
    <el-button type="primary" text @click.stop="handleOpenDialog">
      <MkIcon name="icon-key_outlined" />
    </el-button>
  </MkTooltip>
  <UserPwdDialog ref="dialogRef" @refresh="emit('refresh')" />
</template>
