<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type LogicFlow from '@logicflow/core'
import type { DefaultModelSettingPayload } from '@/api/types'
import AiGeneratePanel from '@/workflow-canvas/ai-generate/panel/AiGeneratePanel.vue'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'ButtonAiGenerate' })
const props = defineProps<{
  label: string
  disabled?: boolean
  getLogicFlow: () => LogicFlow | undefined
  defaultModelSettings: DefaultModelSettingPayload
}>()
const emit = defineEmits<{ open: [] }>()
const aiGeneratePanelRef = useTemplateRef<InstanceType<typeof AiGeneratePanel>>('aiGeneratePanelRef')

/* 打开生成面板前通知页面关闭调试。 */
function handleOpenAiGenerate() {
  if (props.disabled) return
  emit('open')
  aiGeneratePanelRef.value?.open()
}
</script>

<template>
  <!-- AI 生成智能体工作流 -->
  <el-button plain :disabled="disabled" @click="handleOpenAiGenerate">
    <!-- // TODO 图标 -->
    <MkIcon name="icon_star_colorful" />
    <span>{{ label }}</span>
  </el-button>
  <AiGeneratePanel
    ref="aiGeneratePanelRef"
    :get-logic-flow="getLogicFlow"
    :default-model-settings="defaultModelSettings"
    :workflow-mode="WorkflowMode.Application"
  />
</template>
