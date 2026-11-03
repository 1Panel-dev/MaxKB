<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import ChatUserApi from '@/api/chat/chat-user'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'ConversationApiKeyDialog' })

const router = useRouter()
const dialogVisible = ref(false)
const apiKey = ref('')
const loading = ref(false)
const mcpServiceType = ref<'agent' | 'knowledge'>('agent')
const apiUrl = computed(() => new URL(router.resolve({ name: 'portal-home' }).href, window.location.origin).href)
const maskedApiKey = computed(() => (apiKey.value ? `******${apiKey.value.slice(-4)}` : ''))

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
    <el-input :model-value="maskedApiKey" readonly class="mb-4">
      <template #suffix>
        <!-- 复制 API URL -->
        <el-button text @click="copyText(maskedApiKey)">
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
    <!-- 切换 MCP 服务类型 -->
    <el-radio-group v-model="mcpServiceType" class="mb-2">
      <el-radio-button value="agent">智能体对话</el-radio-button>
      <el-radio-button value="knowledge">知识库检索</el-radio-button>
    </el-radio-group>

    <div class="group relative">
      <el-input :model-value="maskedApiKey" readonly :autosize="{ minRows: 8, maxRows: 24 }" type="textarea" />
      <!-- 复制 MCP 配置 -->
      <el-button class="group-hover-visible absolute right-3 top-3 z-10 shadow-md" circle @click="copyText(maskedApiKey)">
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>
