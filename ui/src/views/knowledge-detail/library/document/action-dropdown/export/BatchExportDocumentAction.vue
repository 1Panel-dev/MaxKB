<script setup lang="ts">
import { useRoute } from 'vue-router'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { useKnowledgeDetailContext } from '../../../../context'

defineOptions({ name: 'BatchExportDocumentAction' })

const props = defineProps<{ api: typeof DocumentApi; documentIds: string[]; label: string }>()
const route = useRoute()
const { knowledge } = useKnowledgeDetailContext()
const loading = defineModel<boolean>('loading', { default: false })

/* 批量文档导出菜单 */
const exportOptions = [
  { label: '导出文档 Excel', method: 'exportMulDocument' },
  { label: '导出文档 ZIP', method: 'exportMulDocumentZip' },
] as const

// 固定选中文档 ID，批量只选一个文档时仍按批量导出。
function handleExportDocuments(method: (typeof exportOptions)[number]['method']) {
  loading.value = true
  return props.api[method](String(route.params.knowledgeId ?? ''), [...props.documentIds], knowledge.value?.name || '文档')
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <MkDropdownItem divided @click.prevent.stop class="p-0!">
    <MkDropdown class="w-full" trigger="hover" placement="right-start">
      <!-- 展开批量文档导出菜单 -->
      <div class="flex-between w-full gap-2 p-2">
        <span>{{ label }}</span>

        <MkIcon name="icon_right_outlined" class="text-N600!" />
      </div>
      <template #dropdown>
        <MkDropdownMenu>
          <template v-for="exportOption in exportOptions" :key="exportOption.method">
            <!-- 按所选格式批量导出文档 -->
            <MkDropdownItem :disabled="loading" @click="handleExportDocuments(exportOption.method)">
              {{ exportOption.label }}
            </MkDropdownItem>
          </template>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
