<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { formatKnowledgeMcpConfig } from '@/views/knowledge/external-retrieval-config'
import { copyText } from '@/utils/clipboard'
import { isSystemResource, isWorkspaceResource } from '@/utils/resource-context'
import { perm } from '@/permission'

defineOptions({ name: 'McpConfigKnowledgeAction' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi
  knowledge: KnowledgeItem
  label: string
}>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库 MCP 服务配置 */
const visible = ref(false)
const config = ref('')
const canRead = () =>
  isSystemResource() ? perm.knowledge.system.mcpConfig() : !isWorkspaceResource() || perm.knowledge.workspace.mcpConfig(props.knowledge.id)

function handleOpenMcpConfig() {
  if (!canRead() || loading.value) return
  loading.value = true
  return props.api
    .getKnowledgeMcpConfig(props.knowledge.id)
    .then((mcpConfig) => {
      config.value = formatKnowledgeMcpConfig(JSON.parse(mcpConfig), window.location.origin)
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
  <!-- 查看 MCP 服务配置 -->
  <MkDropdownItem v-if="canRead()" :disabled="loading" @click.stop="handleOpenMcpConfig">
    <template #icon><MkIcon name="icon_describe_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <MkDialog v-model="visible" :title="t('resource.mcpConfig.title')" @closed="handleDialogClosed">
    <div class="group relative">
      <el-input v-model="config" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
      <!-- 复制 MCP 配置 -->
      <el-button
        class="group-hover-visible absolute right-3 top-3 z-10 shadow-md"
        circle
        :disabled="!config"
        @click="copyText(config, t('common.messages.copied'))"
      >
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>
