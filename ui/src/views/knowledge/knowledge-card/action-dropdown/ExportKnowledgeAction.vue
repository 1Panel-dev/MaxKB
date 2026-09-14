<script setup lang="ts">
import { isAxiosError } from 'axios'
import { computed, useTemplateRef } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'ExportKnowledgeAction' })

const props = defineProps<{ api: typeof KnowledgeApi; knowledge: KnowledgeItem; label: string }>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库导出菜单 */
const exportTriggerRef = useTemplateRef<HTMLElement>('exportTriggerRef')
// 子菜单挂到一级浮层内，保持焦点包含关系，同时避开菜单滚动区的 overflow 裁剪。
const submenuContainer = computed(() => exportTriggerRef.value?.closest<HTMLElement>('.el-dropdown__popper'))
const exportOptions = [
  { label: '导出文档 Excel', method: 'exportKnowledgeExcel' },
  { label: '导出文档 ZIP', method: 'exportKnowledgeZip' },
  { label: '导出知识库', method: 'exportKnowledge' },
] as const

function handleExportKnowledge(method: (typeof exportOptions)[number]['method']) {
  if (loading.value) return
  loading.value = true
  return props.api[method](props.knowledge.id, props.knowledge.name)
    .catch((error: unknown) => {
      // 下载封装已处理 JSON 成功响应和鉴权错误，此处补充未统一提示的下载失败。
      if (!isAxiosError(error) || error.code === 'ECONNABORTED' || [401, 403, 404].includes(error.response?.status ?? 0)) return
      const responseData: unknown = error.response?.data
      if (responseData instanceof Blob) {
        return responseData.text().then((responseText) => {
          let message = responseText || error.message
          try {
            const response: { message?: unknown } = JSON.parse(responseText)
            if (typeof response?.message === 'string') message = response.message
          } catch {
            // 非 JSON 错误响应保留原始文本。
          }
          MsgError(`导出失败：${message}`)
        })
      }
      MsgError(`导出失败：${error.message}`)
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <MkDropdownItem divided @click.prevent.stop class="p-0!" :disabled="loading">
    <MkDropdown class="w-full" trigger="hover" placement="right-start" :append-to="submenuContainer ?? undefined" :disabled="loading">
      <!-- 展开知识库导出菜单 -->
      <div ref="exportTriggerRef" class="flex-between w-full gap-2 p-2">
        <div class="flex items-center gap-2">
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
