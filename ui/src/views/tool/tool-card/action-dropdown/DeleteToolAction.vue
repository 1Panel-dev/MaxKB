<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'DeleteToolAction' })

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [toolId: string] }>()

function handleDeleteTool() {
  return MsgConfirm(`${t('tool.delete.title')}: ${props.tool.name}?`, undefined, {
    cancelButtonText: t('common.actions.cancel'),
    confirmButtonText: t('common.actions.delete'),
  })
    .then(() => {
      loading.value = true
      return props.api
        .deleteTool(props.tool.id)
        .finally(() => (loading.value = false))
        .then(() => {
          emit('delete', props.tool.id)
          MsgSuccess(t('common.messages.deleteSuccess'))
        })
    })
    .catch(() => {})
}
</script>

<template>
  <!-- 删除工具 -->
  <MkDropdownItem @click="handleDeleteTool">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
