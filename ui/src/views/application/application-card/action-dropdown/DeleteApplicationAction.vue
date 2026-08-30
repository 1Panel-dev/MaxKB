<script setup lang="ts">
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteApplicationAction' })

const props = defineProps<{ api: typeof ApplicationApi; application: ApplicationDetail; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [applicationId: string] }>()

function handleDeleteApplication() {
  return MsgConfirm(`确认删除智能体：${props.application.name}？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      loading.value = true
      return props.api
        .deleteApplication(props.application.id)
        .then(() => {
          emit('delete', props.application.id)
          MsgSuccess('删除成功')
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}
</script>

<template>
  <MkDropdownItem divided @click="handleDeleteApplication">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
