<script setup lang="ts">
import { ref } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type { ToolItem } from '@/api/types'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'McpConfigAction' })

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

/* 工具 MCP 配置展示与复制 */
const visible = ref(false)
const config = ref('')

function handleOpenMcpConfig() {
  loading.value = true
  return props.api
    .getToolDetail(props.tool.id)
    .then((toolDetail) => {
      config.value = toolDetail.code ?? ''
      visible.value = true
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDialogClosed() {
  config.value = ''
}
</script>

<template>
  <!-- 查看 MCP 配置 -->
  <MkDropdownItem @click="handleOpenMcpConfig">
    <template #icon><MkIcon name="icon_describe_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <MkDialog v-model="visible" title="MCP 配置详情" @closed="handleDialogClosed">
    <div class="group relative">
      <el-input v-model="config" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
      <!-- 复制 MCP 配置 -->
      <el-button class="group-hover-visible absolute right-3 top-3 z-10 shadow-md" circle :disabled="!config" @click="copyText(config)">
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>
