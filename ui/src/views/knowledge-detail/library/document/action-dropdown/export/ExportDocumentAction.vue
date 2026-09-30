<script setup lang="ts">
import { useRoute } from 'vue-router'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentItem } from '@/api/types'

defineOptions({ name: 'ExportDocumentAction' })

const props = defineProps<{ api: typeof DocumentApi; document: DocumentItem; label: string }>()
const route = useRoute()
const loading = defineModel<boolean>('loading', { default: false })

/* 文档导出菜单 */
const exportOptions = [
  { label: '导出文档 Excel', method: 'exportDocument' },
  { label: '导出文档 ZIP', method: 'exportDocumentZip' },
] as const

// 导出当前文档，保留列表状态。
function handleExportDocument(method: (typeof exportOptions)[number]['method']) {
  loading.value = true
  return props.api[method](String(route.params.knowledgeId ?? ''), props.document.id, props.document.name)
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <MkDropdownItem divided @click.prevent.stop class="p-0!">
    <MkDropdown class="w-full" trigger="hover" placement="left-start">
      <!-- 展开文档导出菜单 -->
      <div class="flex-between w-full gap-2 p-2">
        <div class="flex-align-center gap-2">
          <MkIcon name="icon_export_outlined" class="text-N600!" />
          <span>{{ label }}</span>
        </div>

        <MkIcon name="icon_right_outlined" class="text-N600!" />
      </div>
      <template #dropdown>
        <MkDropdownMenu>
          <template v-for="exportOption in exportOptions" :key="exportOption.method">
            <!-- 按所选格式导出文档 -->
            <MkDropdownItem :disabled="loading" @click="handleExportDocument(exportOption.method)">
              {{ exportOption.label }}
            </MkDropdownItem>
          </template>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
