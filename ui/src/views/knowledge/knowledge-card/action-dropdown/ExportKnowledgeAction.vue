<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'

defineOptions({ name: 'ExportKnowledgeAction' })

const props = defineProps<{
  api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi
  knowledge: KnowledgeItem
  label: string
}>()
const loading = defineModel<boolean>('loading', { default: false })

// 二级菜单留在所属一级浮层内，避免焦点移入时关闭一级菜单，并避开滚动容器裁剪。
const exportTriggerRef = useTemplateRef<HTMLDivElement>('exportTriggerRef')
const exportMenuContainer = computed(() => exportTriggerRef.value?.closest<HTMLElement>('.el-dropdown__popper'))

/* 知识库导出菜单 */
const exportOptions = [
  { label: '导出文档 Excel', method: 'exportKnowledgeExcel' },
  { label: '导出文档 ZIP', method: 'exportKnowledgeZip' },
  { label: '导出知识库', method: 'exportKnowledge' },
] as const

function handleExportKnowledge(method: (typeof exportOptions)[number]['method']) {
  if (loading.value) return
  loading.value = true
  return props.api[method](props.knowledge.id, props.knowledge.name)
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <MkDropdownItem divided @click.prevent.stop class="p-0!">
    <MkDropdown class="w-full" trigger="hover" placement="right-start" :append-to="exportMenuContainer">
      <!-- 展开知识库导出菜单 -->
      <div ref="exportTriggerRef" class="flex-between w-full gap-2 p-2">
        <div class="flex-align-center gap-2">
          <MkIcon name="icon_export_outlined" class="text-N600!" />
          <span>{{ label }}</span>
        </div>

        <MkIcon name="icon_right_outlined" class="text-N600!" />
      </div>
      <template #dropdown>
        <MkDropdownMenu>
          <!-- 按所选格式导出 -->
          <MkDropdownItem
            v-for="exportOption in exportOptions"
            :key="exportOption.method"
            :disabled="loading"
            @click="handleExportKnowledge(exportOption.method)"
          >
            {{ exportOption.label }}
          </MkDropdownItem>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
