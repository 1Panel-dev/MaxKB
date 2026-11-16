<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type ModelApi from '@/api/admin/workspace/model'
import type { ModelItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'DeleteModelAction' })

const props = defineProps<{ api: typeof ModelApi | typeof SystemSharedModelApi; label: string; model: ModelItem }>()

const emit = defineEmits<{ refresh: [] }>()

function handleDeleteModel() {
  return MsgConfirm(
    t('model.delete.title', { name: props.model.name }),
    props.model.resource_count ? t('model.delete.description', { count: props.model.resource_count }, props.model.resource_count) : '',
  )
    .then(() => {
      return props.api.deleteModel(props.model.id).then(() => {
        emit('refresh')
        MsgSuccess(t('common.messages.deleteSuccess'))
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
