<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail } from '@/api/types'
import CopyApplicationDialog from './CopyApplicationDialog.vue'

defineOptions({ name: 'CopyApplicationAction' })
const props = defineProps<{
  api: typeof ApplicationApi
  application: ApplicationDetail
  folderId: string
  label: string
}>()
const emit = defineEmits<{ refresh: [] }>()
const loading = defineModel<boolean>('loading', { default: false })

// 读取完整配置后挂载复制弹窗，关闭动画结束后卸载。
const dialogMounted = ref(false)
const copyApplicationDialogRef = useTemplateRef<InstanceType<typeof CopyApplicationDialog>>('copyApplicationDialogRef')
function handleCopyApplication() {
  if (loading.value) return
  const folderId = props.folderId
  loading.value = true
  return props.api
    .getApplicationDetail(props.application.id)
    .then((application) => {
      dialogMounted.value = true
      return nextTick(() => copyApplicationDialogRef.value?.open(application, folderId))
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 复制智能体 -->
  <MkDropdownItem :disabled="loading" @click="handleCopyApplication">
    <template #icon><MkIcon name="icon_copy_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <CopyApplicationDialog v-if="dialogMounted" ref="copyApplicationDialogRef" :api="api" @closed="dialogMounted = false" @refresh="emit('refresh')" />
</template>
