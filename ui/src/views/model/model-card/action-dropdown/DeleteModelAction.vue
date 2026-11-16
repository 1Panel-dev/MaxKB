<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type ModelApi from '@/api/admin/workspace/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type { ModelItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteModelAction' })

const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api: typeof ModelApi | typeof SystemSharedModelApi; label: string; model: ModelItem }>()

const emit = defineEmits<{ refresh: [] }>()

function handleDeleteModel() {
  return MsgConfirm(
    t('model.delete.confirm', { name: props.model.name }),
    props.model.resource_count ? t('model.delete.referenced', { count: props.model.resource_count }) : '',
    { cancelButtonText: t('common.actions.cancel'), confirmButtonText: t('common.actions.delete') },
  )
    .then(() => {
      return props.api.deleteModel(props.model.id).then(() => {
        emit('refresh')
        MsgSuccess(t('common.messages.deleted'))
      })
    })
    .catch(() => {})
}
</script>

<template>
  <!-- 删除模型 -->
  <MkDropdownItem @click="handleDeleteModel">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
