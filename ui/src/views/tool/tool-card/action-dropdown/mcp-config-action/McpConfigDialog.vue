<script setup lang="ts">
import { ref } from 'vue'
import type { ToolItem } from '@/api/types'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'McpConfigDialog' })

const emit = defineEmits<{ closed: [] }>()

const visible = ref(false)
const config = ref('')

function open(tool: ToolItem) {
  config.value = tool.code ?? ''
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="MCP 配置详情" @closed="emit('closed')">
    <div class="group mcp-config-detail relative">
      <el-input v-model="config" :autosize="{ minRows: 8, maxRows: 24 }" disabled type="textarea" />
      <el-button class="group-hover-visible absolute right-3 top-3 z-10 h-8 shadow-md" circle title="复制配置" @click="copyText(config)">
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>
<style scoped lang="scss">
.mcp-config-detail {
  :deep(.el-textarea__inner) {
    color: var(--el-text-color-primary);
    cursor: pointer;
  }
}
</style>
