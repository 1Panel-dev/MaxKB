<script setup lang="ts">
import type ModelApi from '@/api/admin/workspace/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type { ModelItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteModelAction' })

const props = defineProps<{ api: typeof ModelApi | typeof SystemSharedModelApi; label: string; model: ModelItem }>()

const emit = defineEmits<{ refresh: [] }>()

function handleDeleteModel() {
  return MsgConfirm(
    `是否删除模型：${props.model.name}？`,
    props.model.resource_count ? `此模型关联 ${props.model.resource_count} 个资源，删除后无法使用，请谨慎操作。` : '',
  )
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
  <!-- 删除模型 -->
  <MkDropdownItem @click="handleDeleteModel">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
