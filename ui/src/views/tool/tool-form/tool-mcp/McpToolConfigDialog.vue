<script setup lang="ts">
import { ref } from 'vue'
import type { ToolItem } from '@/api/types'
import { copyText } from '@/utils/clipboard'

defineOptions({ name: 'McpToolConfigDialog' })

const visible = ref(false)
const config = ref('')

function open(tool: ToolItem) {
  config.value = tool.code ?? ''
  visible.value = true
}

defineExpose({ open })
</script>

<template>
  <MkDialog v-model="visible" title="MCP 配置" width="600">
    <div class="relative">
      <el-input v-model="config" :rows="8" disabled type="textarea" />
      <el-button class="absolute top-2 right-2" circle @click="copyText(config)">
        <MkIcon name="icon_copy_outlined" />
      </el-button>
    </div>
  </MkDialog>
</template>
