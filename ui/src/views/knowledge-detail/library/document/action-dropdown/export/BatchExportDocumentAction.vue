<script setup lang="ts">
import { inject } from 'vue'
import { useRoute } from 'vue-router'
import { DROPDOWN_INJECTION_KEY } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'

defineOptions({ name: 'BatchExportDocumentAction' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']; documentIds: string[]; label: string }>()
const route = useRoute()
const { knowledge } = useKnowledgeDetailContext()
const loading = defineModel<boolean>('loading', { default: false })

// 选中二级导出项后同步收起一级菜单，保留 Action 内的请求和弹窗状态。
const parentDropdown = inject(DROPDOWN_INJECTION_KEY, undefined)

/* 批量文档导出菜单 */
const exportOptions = [
  { labelKey: 'knowledge.export.documentsExcel', method: 'exportMulDocument' },
  { labelKey: 'knowledge.export.documentsZip', method: 'exportMulDocumentZip' },
] as const

// 固定选中文档 ID，批量只选一个文档时仍按批量导出。
function handleExportDocuments(method: (typeof exportOptions)[number]['method']) {
  loading.value = true
  return (
    props.api[method]?.(String(route.params.knowledgeId ?? ''), [...props.documentIds], knowledge.value?.name || '文档').catch(() => {}) ??
    Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <MkDropdownItem @click.prevent.stop class="p-0!">
    <MkDropdown @command="parentDropdown?.handleClose()" class="w-full" trigger="hover" placement="right-start">
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
              {{ t(exportOption.labelKey) }}
            </MkDropdownItem>
          </template>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
