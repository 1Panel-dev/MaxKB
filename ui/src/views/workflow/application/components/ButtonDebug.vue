<script setup lang="ts">
import { useTemplateRef } from 'vue'
import DebugPanel from '@/conversation-panel/view/debug/index.vue'

defineOptions({ name: 'ButtonDebug' })
const props = defineProps<{
  label: string
  disabled?: boolean
  hasUnsavedChanges: () => boolean
  saveWorkflow: () => Promise<unknown>
}>()
const loading = defineModel<boolean>('loading', { default: false })
const debugPanelRef = useTemplateRef<InstanceType<typeof DebugPanel>>('debugPanelRef')

/* 调试前保存未提交修改；保存失败时保留画布，不打开调试。 */
async function handleDebug() {
  if (loading.value || props.disabled) return
  if (props.hasUnsavedChanges()) {
    loading.value = true
    try {
      await props.saveWorkflow()
    } catch {
      // 保存失败已由页面保存流程提示。
      return
    } finally {
      loading.value = false
    }
  }
  debugPanelRef.value?.open()
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
  <DebugPanel ref="debugPanelRef" />
</template>
