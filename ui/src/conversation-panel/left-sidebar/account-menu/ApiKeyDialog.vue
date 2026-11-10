<script setup lang="ts">
import { ref, computed } from 'vue'
import ChatUserApi from '@/api/chat/chat-user'
import { CHAT_API_BASE_PATH } from '@/api/constants'
import { useStore } from '@/stores/chat'
import { copyText } from '@/utils/clipboard'
import { useViewType, VIEW_TYPE } from '@/conversation-panel/view'
import { useMessageListStore } from '@/conversation-panel/components/message-list'

defineOptions({ name: 'ConversationApiKeyDialog' })

type McpServiceType = 'agent' | 'knowledge'

const dialogVisible = ref(false)
const apiKey = ref('')
const loading = ref(false)
const mcpServiceType = ref<McpServiceType>('agent')
const { auth } = useStore()
const messageList = useMessageListStore()
const applicationId = computed(() => messageList.appInfo.value?.id)
const viewType = useViewType()

// MCP 地址按当前部署地址拼接对话端 v3 接口；均以当前对话用户的 API Key 认证。
const MCP_BASE_URL = `${window.location.origin}${CHAT_API_BASE_PATH}/v3`

function formatMcpConfig(serverName: string, url: string) {
  return JSON.stringify({ [serverName]: { url, transport: 'streamable_http', headers: { Authorization: `Bearer <CHAT_USER_API_KEY>` } } }, null, 2)
}

// 门户：智能体对话暴露该用户可访问的全部智能体，知识库检索暴露其可访问的全部知识库。
const mcpConfig = computed<Record<McpServiceType, string>>(() => ({
  agent: formatMcpConfig('maxkb_agent', `${MCP_BASE_URL}/mcp`),
  knowledge: formatMcpConfig('maxkb_knowledge', `${MCP_BASE_URL}/knowledge_mcp`),
}))
// 单应用对话：只暴露当前智能体；服务名用对话链接中的 accessToken，比应用 ID 短。
const agentMcpConfig = computed(() => formatMcpConfig(`agent_${auth.accessToken}`, `${MCP_BASE_URL}/application/${applicationId.value}/mcp`))
// 每次打开重新读取；重置直接替换当前用户的唯一密钥。
function loadApiKey(regenerate = false) {
  if (loading.value) return
  loading.value = true
  return (regenerate ? ChatUserApi.postApiKey() : ChatUserApi.getApiKey())
    .then((record) => {
      if (dialogVisible.value) apiKey.value = record.secret_key
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function open() {
  dialogVisible.value = true
  return loadApiKey()
}

function resetData() {
  apiKey.value = ''
  mcpServiceType.value = 'agent'
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="dialogVisible" title="API Key" @closed="resetData">
    <template #subtitle>每个用户仅一个 API Key，绑定当前对话用户、与其同权。重置后旧 Key 立即失效</template>

    <div class="mb-2">我的 API Key</div>
    <el-input :model-value="`******${apiKey.slice(-4)}`" readonly class="mb-4">
      <template #suffix>
        <!-- 复制 API URL -->
        <el-button text @click="copyText(apiKey)">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
        <MkTooltip content="重新生成" placement="top">
          <!-- 重新生成 API Key -->
          <el-button text class="-mr-1" :loading="loading" @click="loadApiKey(true)">
            <MkIcon name="icon_refresh_outlined" />
          </el-button>
        </MkTooltip>
      </template>
    </el-input>

    <div class="mb-2">MCP 服务配置</div>
    <template v-if="viewType === VIEW_TYPE.PORTAL">
      <!-- 切换 MCP 服务类型 -->
      <el-radio-group v-model="mcpServiceType" class="mb-2">
        <el-radio-button value="agent">智能体对话</el-radio-button>
        <el-radio-button value="knowledge">知识库检索</el-radio-button>
      </el-radio-group>
      <div class="group relative">
        <el-input :model-value="mcpConfig[mcpServiceType]" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
        <!-- 复制 MCP 配置 -->
        <el-button class="group-hover-visible absolute right-3 top-3 z-10 shadow-md" circle @click="copyText(mcpConfig[mcpServiceType].replace('<CHAT_USER_API_KEY>',apiKey))">
          <MkIcon name="icon_copy_outlined" />
        </el-button>
      </div>
    </template>
    <div v-else class="group relative">
      <el-input :model-value="agentMcpConfig" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
      <!-- 复制 MCP 配置 -->
      <el-button class="group-hover-visible absolute right-3 top-3 z-10 shadow-md" circle @click="copyText(agentMcpConfig.replace('<CHAT_USER_API_KEY>',apiKey))">
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>
