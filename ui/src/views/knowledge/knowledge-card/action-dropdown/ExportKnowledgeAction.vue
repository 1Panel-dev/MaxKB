<script setup lang="ts">
import { computed, inject, reactive, ref, useTemplateRef } from 'vue'
import { DROPDOWN_INJECTION_KEY } from 'element-plus'
import { useI18n } from 'vue-i18n'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'

defineOptions({ name: 'ExportKnowledgeAction' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi
  knowledge: KnowledgeItem
  label: string
}>()
const loading = defineModel<boolean>('loading', { default: false })

// 选中二级导出项后同步收起一级菜单，保留 Action 内的请求和弹窗状态。
const parentDropdown = inject(DROPDOWN_INJECTION_KEY, undefined)

// 二级菜单留在所属一级浮层内，避免焦点移入时关闭一级菜单，并避开滚动容器裁剪。
const exportTriggerRef = useTemplateRef<HTMLDivElement>('exportTriggerRef')
const exportMenuContainer = computed(() => exportTriggerRef.value?.closest<HTMLElement>('.el-dropdown__popper'))

/* 知识库导出菜单 */
const exportOptions = reactive([
  { label: computed(() => t('knowledge.export.documentsExcel')), method: 'exportKnowledgeExcel' },
  { label: computed(() => t('knowledge.export.documentsZip')), method: 'exportKnowledgeZip' },
  { label: computed(() => t('knowledge.export.title')), method: 'exportKnowledge' },
] as const)

const exportDialogVisible = ref(false)
const withSourceFile = ref(false)

function handleExportKnowledge(method: (typeof exportOptions)[number]['method']) {
  if (loading.value) return
  if (method === 'exportKnowledge') {
    exportDialogVisible.value = true
    return
  }
  loading.value = true
  return props.api[method](props.knowledge.id, props.knowledge.name)
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

/* 确定知识库压缩包是否包含源文件 */
function handleConfirmExport() {
  if (loading.value) return
  loading.value = true
  return props.api
    .exportKnowledge(props.knowledge.id, props.knowledge.name, withSourceFile.value)
    .then((success) => {
      if (success) exportDialogVisible.value = false
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleExportDialogClosed() {
  withSourceFile.value = false
}
</script>

<template>
  <MkDropdownItem @click.prevent.stop class="p-0!">
    <MkDropdown @command="parentDropdown?.handleClose()" class="w-full" trigger="hover" placement="right-start" :append-to="exportMenuContainer">
      <!-- 展开知识库导出菜单 -->
      <div ref="exportTriggerRef" class="flex-between w-full gap-2 py-[5px] px-2">
        <div class="flex-align-center gap-2">
          <MkIcon name="icon_export_outlined" class="text-N600!" />
          <span>{{ label }}</span>
        </div>

        <MkIcon name="icon_right_outlined" class="text-N500!" />
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

  <MkDialog v-model="exportDialogVisible" :title="t('knowledge.export.title')" width="420" @closed="handleExportDialogClosed">
    <div v-loading="loading">
      <!-- 选择是否同时导出源文件 -->
      <el-checkbox v-model="withSourceFile">{{ t('knowledge.export.includeSourceFiles') }}</el-checkbox>
      <p class="ml-6 text-N600">{{ t('knowledge.export.sourceFilesDescription') }}</p>
    </div>
    <template #footer>
      <!-- 取消导出知识库 -->
      <el-button plain :disabled="loading" @click="exportDialogVisible = false">{{ t('common.actions.cancel') }}</el-button>
      <!-- 确定导出知识库 -->
      <el-button type="primary" :loading="loading" @click="handleConfirmExport">{{ t('common.actions.export') }}</el-button>
    </template>
  </MkDialog>
</template>
