<script setup lang="ts">
import type ModelApi from '@/api/admin/workspace/model/model'
import type { ModelItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteModelAction' })

const props = defineProps<{ api: typeof ModelApi; label: string; model: ModelItem }>()

const emit = defineEmits<{ refresh: [] }>()

function handleDeleteModel() {
  return MsgConfirm(`确认删除模型：${props.model.name}？`)
    .then(() => {
      return props.api.deleteModel(props.model.id).then(() => {
        emit('refresh')
        MsgSuccess('删除成功')
      })
    })
    .catch(() => {})
}
</script>

<template>
  <MkDropdownItem divided @click="handleDeleteModel">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
