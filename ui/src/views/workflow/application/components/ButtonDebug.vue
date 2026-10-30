<script setup lang="ts">
import { useTemplateRef } from 'vue'
import DebugPanel from '@/conversation-panel/view/debug/index.vue'
import type { ApplicationDetail } from '@/api/types'
import { showWorkflowValidateError } from '../../components/validate-error'

defineOptions({ name: 'ButtonDebug' })
const props = defineProps<{
  label: string
  disabled?: boolean
  hasUnsavedChanges: () => boolean
  validateWorkflow: () => Promise<unknown>
  saveWorkflow: () => Promise<unknown>
  /** 当前智能体详情，保存后由工作流页更新，调试面板据此展示开场白等配置。 */
  application?: ApplicationDetail | null
}>()
const loading = defineModel<boolean>('loading', { default: false })
const debugPanelRef = useTemplateRef<InstanceType<typeof DebugPanel>>('debugPanelRef')

/* 每次打开调试前校验画布，有未提交修改时再保存；失败时不打开调试。 */
async function handleDebug() {
  if (loading.value || props.disabled) return
  loading.value = true
  try {
    await props.validateWorkflow().catch((error: unknown) => {
      showWorkflowValidateError(error)
      throw error
    })
    if (props.hasUnsavedChanges()) await props.saveWorkflow()
    debugPanelRef.value?.open()
  } catch {
    // 校验或保存失败已由对应流程提示。
    return
  } finally {
    loading.value = false
  }
}

function close() {
  debugPanelRef.value?.close()
}

defineExpose({ close })
</script>

<template>
  <!-- 调试智能体工作流 -->
  <MkTooltip :content="label" placement="bottom">
    <el-button plain :disabled="loading || disabled" @click="handleDebug" class="w-8! min-w-8!">
      <MkIcon name="icon_play_outlined" />
    </el-button>
  </MkTooltip>
  <DebugPanel ref="debugPanelRef" :application="application" />
</template>
