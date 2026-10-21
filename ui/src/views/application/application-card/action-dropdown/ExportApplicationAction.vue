<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import type { ApplicationDetail, ExportError } from '@/api/types'
import { MsgError, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ExportApplicationAction' })

const props = defineProps<{ api: typeof ApplicationApi | typeof SystemResourceApplicationApi; application: ApplicationDetail; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

// 二级菜单留在所属一级浮层内，避免焦点移入时关闭一级菜单，并避开滚动容器裁剪。
const exportTriggerRef = useTemplateRef<HTMLDivElement>('exportTriggerRef')
const exportMenuContainer = computed(() => exportTriggerRef.value?.closest<HTMLElement>('.el-dropdown__popper'))

function handleExportSkills() {
  if (loading.value) return
  loading.value = true
  return props.api
    .exportApplicationSkills(props.application.id, props.application.name)
    .then(() => {
      MsgSuccess('Skills 导出已模拟完成，暂不生成文件')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleExportApplication() {
  if (loading.value) return
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
  <MkDropdownItem @click.prevent.stop class="p-0!">
    <MkDropdown class="w-full" trigger="hover" placement="right-start" :append-to="exportMenuContainer">
      <!-- 展开智能体导出菜单 -->
      <div ref="exportTriggerRef" class="flex-between w-full gap-2 p-2">
        <div class="flex-align-center gap-2">
          <MkIcon name="icon_export_outlined" class="text-N600!" />
          <span>{{ label }}</span>
        </div>
        <MkIcon name="icon_right_outlined" class="text-N600!" />
      </div>
      <template #dropdown>
        <MkDropdownMenu>
          <!-- 模拟导出为 Skills -->
          <MkDropdownItem :disabled="loading" @click="handleExportSkills">导出为 Skills</MkDropdownItem>
          <!-- 导出智能体文件 -->
          <MkDropdownItem :disabled="loading" @click="handleExportApplication">导出智能体</MkDropdownItem>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
