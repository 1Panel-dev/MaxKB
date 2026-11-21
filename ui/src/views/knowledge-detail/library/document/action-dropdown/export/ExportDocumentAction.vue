<script setup lang="ts">
import { computed, inject, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { DROPDOWN_INJECTION_KEY } from 'element-plus'
import { useI18n } from 'vue-i18n'
import type { DocumentItem } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'

defineOptions({ name: 'ExportDocumentAction' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']; document: DocumentItem; label: string }>()
const route = useRoute()
const loading = defineModel<boolean>('loading', { default: false })

// 选中二级导出项后同步收起一级菜单，保留 Action 内的请求和弹窗状态。
const parentDropdown = inject(DROPDOWN_INJECTION_KEY, undefined)

/* 文档导出菜单 */
const exportOptions = reactive([
  { label: computed(() => t('knowledge.export.documentsExcel')), method: 'exportDocument' },
  { label: computed(() => t('knowledge.export.documentsZip')), method: 'exportDocumentZip' },
] as const)

// 导出当前文档，保留列表状态。
function handleExportDocument(method: (typeof exportOptions)[number]['method']) {
  loading.value = true
  return (
    props.api[method]?.(String(route.params.knowledgeId ?? ''), props.document.id, props.document.name).catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <MkDropdownItem @click.prevent.stop class="p-0!">
    <MkDropdown @command="parentDropdown?.handleClose()" class="w-full" trigger="hover" placement="left-start">
      <!-- 展开文档导出菜单 -->
      <div class="flex-between w-full gap-2 py-[5px] px-2">
        <div class="flex-align-center gap-2">
          <MkIcon name="icon_export_outlined" class="text-N600!" />
          <span>{{ label }}</span>
        </div>

        <MkIcon name="icon_right_outlined" class="text-N500!" />
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
