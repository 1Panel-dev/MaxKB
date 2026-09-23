<script setup lang="ts">
import { ref } from 'vue'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'KnowledgeMcpConfigDialog' })

const emit = defineEmits<{ closed: [] }>()

/* 配置展示与复制 */
const visible = ref(false)
const config = ref('')

function open(mcpConfig: string) {
  config.value = mcpConfig
  visible.value = true
}

function handleClosed() {
  config.value = ''
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="MCP 配置详情" @closed="handleClosed">
    <div class="group knowledge-mcp-config-detail relative">
      <el-input v-model="config" :autosize="{ minRows: 8, maxRows: 24 }" disabled type="textarea" />
      <!-- 复制 MCP 配置 -->
      <el-button
        class="group-hover-visible absolute right-3 top-3 z-10 shadow-md"
        circle
        title="复制配置"
        :disabled="!config"
        @click="copyText(config)"
      >
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>

<style scoped lang="scss">
.knowledge-mcp-config-detail {
  :deep(.el-textarea__inner) {
    color: var(--el-text-color-primary);
    cursor: pointer;
  }
}
</style>
