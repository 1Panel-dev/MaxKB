<script setup lang="ts">
import { computed, ref } from 'vue'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import type { ApplicationDetail } from '@/api/types'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'McpConfigApplicationAction' })

const props = defineProps<{ application: ApplicationDetail; label: string }>()

/* 单个智能体的 MCP 服务配置：地址带智能体 id，仅暴露该智能体，使用对话用户 API Key 认证 */
const visible = ref(false)
const mcpUrl = computed(() => new URL(`${CHAT_API_BASE_PATH}/v3/application/${props.application.id}/mcp`, window.location.origin).href)
const mcpConfig = computed(() =>
  JSON.stringify(
    {
      [`agent_${props.application.id}`]: {
        url: mcpUrl.value,
        transport: 'streamable_http',
        headers: { Authorization: 'Bearer <CHAT_USER_API_KEY>' },
      },
    },
    null,
    2,
  ),
)

function handleOpenMcpConfig() {
  visible.value = true
}
</script>

<template>
  <!-- 查看智能体 MCP 服务配置 -->
  <MkDropdownItem :disabled="!application.is_publish" @click.stop="handleOpenMcpConfig">
    <template #icon><MkIcon name="icon_describe_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <MkDialog v-model="visible" title="MCP 服务配置">
    <div class="group relative">
      <el-input :model-value="mcpConfig" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
      <!-- 复制 MCP 配置 -->
      <el-button class="group-hover-visible absolute right-3 top-3 z-10 shadow-md" circle @click="copyText(mcpConfig)">
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>
