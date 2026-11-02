<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type LogicFlow from '@logicflow/core'
import type WorkflowApi from '@/api/admin/workspace/tool/workflow'
import DebugDrawer from '../debug/DebugDrawer.vue'
import { showWorkflowValidateError } from '../../components/validate-error'

defineOptions({ name: 'ButtonDebug' })

const props = defineProps<{
  label: string
  api: typeof WorkflowApi
  toolId: string
  disabled?: boolean
  hasUnsavedChanges: () => boolean
  validateWorkflow: () => Promise<unknown> | undefined
  saveWorkflow: () => Promise<unknown>
  getGraphData: () => LogicFlow.GraphData | undefined
}>()
const loading = defineModel<boolean>('loading', { default: false })
const debugDrawerRef = useTemplateRef<InstanceType<typeof DebugDrawer>>('debugDrawerRef')

/* 每次打开调试前校验画布，有未提交修改时再保存；失败时不打开调试。 */
async function handleDebug() {
  if (loading.value || props.disabled) return
  try {
    const validation = props.validateWorkflow()
    if (!validation) return
    loading.value = true
    await validation.catch((error: unknown) => {
      showWorkflowValidateError(error)
      throw error
    })
    if (props.hasUnsavedChanges()) await props.saveWorkflow()
    const graphData = props.getGraphData()
    if (graphData) debugDrawerRef.value?.open(graphData)
  } catch {
    // 校验或保存失败已由对应流程提示，不打开调试。
  } finally {
    loading.value = false
  }
}

function close() {
  debugDrawerRef.value?.close()
}

defineExpose({ close })
</script>

<template>
  <!-- 调试工具工作流 -->
  <MkTooltip :content="label" placement="bottom">
    <el-button plain :disabled="loading || disabled" @click="handleDebug" class="w-8! min-w-8!">
      <MkIcon name="icon_play_outlined" />
    </el-button>
  </MkTooltip>
  <DebugDrawer ref="debugDrawerRef" :api="api" :tool-id="toolId" />
</template>
