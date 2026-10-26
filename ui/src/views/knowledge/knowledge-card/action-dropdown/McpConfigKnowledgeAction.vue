<script setup lang="ts">
import { perm } from '@/permission'
import { isSystemResource, isWorkspaceResource } from '@/utils/resource-context'
import { ref } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { copyText } from '@/utils/clipboard'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'

defineOptions({ name: 'McpConfigKnowledgeAction' })

const props = defineProps<{
  api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi
  knowledge: KnowledgeItem
  label: string
}>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库 MCP 配置详情 */
const visible = ref(false)
const config = ref('')
const canRead = () => isSystemResource() ? perm.knowledge.system.mcpConfig() : !isWorkspaceResource() || perm.knowledge.workspace.mcpConfig(props.knowledge.id)

function handleOpenMcpConfig() {
  if (!canRead() || loading.value) return
  loading.value = true
  return props.api
    .getKnowledgeMcpConfig(props.knowledge.id)
    .then((mcpConfig) => {
      config.value = mcpConfig
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
  <!-- 查看 MCP 配置详情 -->
  <MkDropdownItem v-if="canRead()" :disabled="loading" @click.stop="handleOpenMcpConfig">
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
