<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { ElMessageBox } from 'element-plus'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import type { ApplicationDetail, ExportError } from '@/api/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'ExportApplicationAction' })

const props = defineProps<{ api: typeof ApplicationApi | typeof SystemResourceApplicationApi; application: ApplicationDetail; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

// 二级菜单留在所属一级浮层内，避免焦点移入时关闭一级菜单，并避开滚动容器裁剪。
const exportTriggerRef = useTemplateRef<HTMLDivElement>('exportTriggerRef')
const exportMenuContainer = computed(() => exportTriggerRef.value?.closest<HTMLElement>('.el-dropdown__popper'))

/** 让用户填写写入 Skills 的 MaxKB 访问地址。 */
function promptSkillsBaseUrl(baseUrl: string) {
  return ElMessageBox.prompt('请填写 Agent 访问 MaxKB 使用的地址，例如 http://192.168.1.10:8080', '填写访问地址', {
    inputValue: baseUrl,
    inputPattern: /^https?:\/\/\S+$/,
    inputErrorMessage: '请填写以 http:// 或 https:// 开头的地址',
    confirmButtonText: '导出',
    cancelButtonText: '取消',
  }).then(({ value }) => value.trim())
}

/** 按访问地址导出 Skills；后端判定地址无效（400）时让用户重新填写后再导出。 */
function exportSkills(baseUrl: string): Promise<unknown> {
  return props.api.exportApplicationSkills(props.application.id, props.application.name, baseUrl).catch((error: ExportError) => {
    const status = error.response?.status
    if (status === 400) return promptSkillsBaseUrl(baseUrl).then(exportSkills)
    if (status && status !== 403) {
      return error.response.data.text().then((response: string) => {
        MsgError(`导出失败：${JSON.parse(response).message}`)
      })
    }
  })
}

function handleExportSkills() {
  if (loading.value) return
  loading.value = true
  // 默认使用当前页面地址，取不到时先让用户填写
  const origin = window.location.origin
  const baseUrl = origin && origin !== 'null' ? Promise.resolve(origin) : promptSkillsBaseUrl('')
  return (
    baseUrl
      .then(exportSkills)
      // 用户取消填写时静默结束
      .catch(() => {})
      .finally(() => {
        loading.value = false
      })
  )
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
          <!-- 导出为 Skills 压缩包 -->
          <MkDropdownItem :disabled="loading" @click="handleExportSkills">导出为 Skills</MkDropdownItem>
          <!-- 导出智能体文件 -->
          <MkDropdownItem :disabled="loading" @click="handleExportApplication">导出智能体</MkDropdownItem>
        </MkDropdownMenu>
      </template>
    </MkDropdown>
  </MkDropdownItem>
</template>
