<script setup lang="ts">
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail, ExportError } from '@/api/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'ExportApplicationAction' })

const props = defineProps<{ api: typeof ApplicationApi; application: ApplicationDetail; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

function handleExportApplication() {
  loading.value = true
  return props.api
    .exportApplication(props.application.id, props.application.name)
    .catch((error: ExportError) => {
      if (error.response.status !== 403) {
        return error.response.data.text().then((response: string) => {
          MsgError(`导出失败：${JSON.parse(response).message}`)
        })
      }
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <MkDropdownItem divided @click="handleExportApplication">
    <template #icon><MkIcon name="icon_export_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
