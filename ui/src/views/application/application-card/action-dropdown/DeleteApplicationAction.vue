<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteApplicationAction' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api: typeof ApplicationApi | typeof SystemResourceApplicationApi; application: ApplicationDetail; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [applicationId: string] }>()

function handleDeleteApplication() {
  return MsgConfirm(`${t('application.delete.title')}: ${props.application.name}?`, t('common.dialogs.deleteWarning'))
    .then(() => {
      loading.value = true
      return props.api
        .deleteApplication(props.application.id)
        .finally(() => {
          loading.value = false
        })
        .then(() => {
          emit('delete', props.application.id)
          MsgSuccess(t('common.messages.deleteSuccess'))
        })
    })
    .catch(() => {})
}
</script>

<template>
  <MkDropdownItem @click="handleDeleteApplication">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
