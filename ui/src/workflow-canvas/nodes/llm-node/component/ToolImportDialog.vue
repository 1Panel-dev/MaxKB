<script setup lang="ts">
import { ref } from 'vue'
import { normalizeTool, type LlmTool } from '../types'

defineOptions({ name: 'WorkflowLlmToolImportDialog' })

const emit = defineEmits<{ submit: [tools: LlmTool[]] }>()
const visible = ref(false)
const importJson = ref('')
const importError = ref('')

function open() {
  visible.value = true
}

function close() {
  visible.value = false
}

function handleImport() {
  importError.value = ''
  try {
    const parsed = JSON.parse(importJson.value) as unknown
    const imported = (Array.isArray(parsed) ? parsed : [parsed]).map(normalizeTool).filter((tool) => tool !== null)
    if (!imported.length) {
      importError.value = '未找到有效的工具定义'
      return
    }
    emit('submit', imported)
  } catch {
    importError.value = 'JSON 解析失败，请检查格式'
  }
}

function resetData() {
  importJson.value = ''
  importError.value = ''
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" title="导入工具" @closed="resetData">
    <el-input
      v-model="importJson"
      type="textarea"
      :rows="12"
      @paste.stop
      placeholder='粘贴 OpenAI tools 格式 JSON，例如：
[
  {
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "获取天气",
      "parameters": {
        "type": "object",
        "properties": { "location": { "type": "string", "description": "城市" } },
        "required": ["location"]
      }
    }
  }
]'
    />
    <div v-if="importError" class="mt-2 text-sm text-danger">{{ importError }}</div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button plain @click="close">取消</el-button>
      <!-- 批量导入工具 -->
      <el-button type="primary" @click="handleImport">导入</el-button>
    </template>
  </MkDialog>
</template>
