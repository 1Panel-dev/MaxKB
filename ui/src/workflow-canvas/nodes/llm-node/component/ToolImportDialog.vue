<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LlmTool } from '../types'
import { normalizeTool } from '../types'

defineOptions({ name: 'WorkflowLlmToolImportDialog' })

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits<{ submit: [tools: LlmTool[]] }>()
const visible = ref(false)
const importJson = ref('')
const importError = ref('')
const importPlaceholder = computed(
  () => `${t('workflow.llm.toolImport.placeholder')}
${JSON.stringify(
  [
    {
      type: 'function',
      function: {
        name: 'get_weather',
        description: t('workflow.llm.toolImport.weatherDescription'),
        parameters: {
          type: 'object',
          properties: { location: { type: 'string', description: t('workflow.llm.toolImport.cityDescription') } },
          required: ['location'],
        },
      },
    },
  ],
  null,
  2,
)}`,
)

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
      importError.value = t('workflow.llm.toolImport.invalidMessage')
      return
    }
    emit('submit', imported)
  } catch {
    importError.value = t('workflow.llm.jsonParse.invalidMessage')
  }
}

function resetData() {
  importJson.value = ''
  importError.value = ''
}

defineExpose({ open, close })
</script>

<template>
  <MkDialog v-model="visible" :title="t('workflow.llm.toolImport.title')" @closed="resetData">
    <el-input v-model="importJson" type="textarea" :rows="12" @paste.stop :placeholder="importPlaceholder" />
    <div v-if="importError" class="mt-2 text-sm text-danger">{{ importError }}</div>
    <template #footer>
      <!-- 取消导入 -->
      <el-button plain @click="close">{{ t('common.actions.cancel') }}</el-button>
      <!-- 批量导入工具 -->
      <el-button type="primary" @click="handleImport">{{ t('common.actions.import') }}</el-button>
    </template>
  </MkDialog>
</template>
