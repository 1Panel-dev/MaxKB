<script setup lang="ts">
import { nextTick, onMounted, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { cloneDeep } from 'lodash'
import ToolApi from '@/api/admin/workspace/tool/tool'
import ToolWorkflowApi from '@/api/admin/workspace/tool/workflow'
import { RESOURCE_TYPE } from '@/api/enums'
import type { ToolItem, ToolWorkflowDetail } from '@/api/types'
import { datetimeFormat } from '@/utils/time'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultToolNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode, type ShapeItem } from '@/workflow-canvas/types'
import WorkflowComponentMenu from './components/WorkflowComponentMenu.vue'

defineOptions({ name: 'ToolWorkflowView' })

const DEFAULT_WORKFLOW: LogicFlow.GraphConfigData = {
  nodes: cloneDeep(defaultToolNodes),
  edges: [],
}

const route = useRoute()
const router = useRouter()
const toolId = route.params.toolId as string
const workspaceId = route.params.workspaceId as string

const workflowRef = useTemplateRef<InstanceType<typeof WorkflowCanvas>>('workflowRef')

/* 添加工作流组件 */
function handleAddNode(shapeItem: ShapeItem) {
  workflowRef.value?.addNode(shapeItem)
}

function handleDragNode(shapeItem: ShapeItem, event: PointerEvent) {
  workflowRef.value?.onmousedown(shapeItem, event)
}

/* 工具工作流加载与保存 */
const toolDetail = ref<ToolItem>()
const loading = ref(false)
const saving = ref(false)
const savedWorkflow = ref<LogicFlow.GraphData>()
const saveTime = ref<Date | string>()

function getGraphData() {
  return workflowRef.value?.getGraphData()
}

function setSavedWorkflow(graphData: LogicFlow.GraphData) {
  savedWorkflow.value = cloneDeep(graphData)
}

function hasUnsavedChanges() {
  const graphData = getGraphData()
  if (!graphData || !savedWorkflow.value) return false

  return JSON.stringify(graphData) !== JSON.stringify(savedWorkflow.value)
}

function saveToolWorkflow(graphData = getGraphData(), showMessage = false) {
  if (!graphData) return Promise.resolve<ToolWorkflowDetail | undefined>(undefined)

  saving.value = true
  return ToolWorkflowApi.putToolWorkflow(toolId, { work_flow: graphData })
    .then((toolWorkflow) => {
      saveTime.value = toolWorkflow.update_time || new Date()
      setSavedWorkflow(graphData)
      if (showMessage) MsgSuccess('保存成功')
      return toolWorkflow
    })
    .finally(() => {
      saving.value = false
    })
}

function handleSave() {
  saveToolWorkflow(undefined, true)
}

function loadToolWorkflow() {
  loading.value = true
  return Promise.all([ToolApi.getToolDetail(toolId), ToolWorkflowApi.getToolWorkflow(toolId)])
    .then(([tool, toolWorkflow]) => {
      toolDetail.value = tool
      saveTime.value = toolWorkflow.update_time

      const workflow = toolWorkflow.work_flow?.nodes?.length ? toolWorkflow.work_flow : DEFAULT_WORKFLOW
      workflowRef.value?.render(cloneDeep(workflow))

      return nextTick().then(() => {
        const graphData = getGraphData()
        if (graphData) setSavedWorkflow(graphData)
        workflowRef.value?.fitView()
      })
    })
    .finally(() => {
      loading.value = false
    })
}

/* 退出工具工作流 */
function goBack() {
  const folderId = toolDetail.value?.folder_id
  router.push({
    name: 'workspace-tools',
    params: { workspaceId },
    query: folderId ? { folderId } : undefined,
  })
}

function handleBack() {
  if (!hasUnsavedChanges()) {
    goBack()
    return
  }

  // 保存失败时保留当前页面，避免丢失尚未写入服务端的画布数据。
  MsgConfirm('当前工作流尚未保存，是否保存后退出？', undefined, {
    cancelButtonText: '直接退出',
    confirmButtonText: '保存并退出',
    confirmButtonType: 'primary',
    distinguishCancelAndClose: true,
  })
    .then(() => {
      return saveToolWorkflow(undefined, true).then(() => goBack())
    })
    .catch((action: Action) => {
      if (action === 'cancel') goBack()
    })
}

onMounted(() => {
  loadToolWorkflow()
})
</script>

<template>
  <main v-loading="loading" class="flex h-screen w-screen flex-col overflow-hidden">
    <header class="h-header flex-between shrink-0 gap-3 border-b bg-white px-6">
      <div class="flex min-w-0 items-center gap-3">
        <el-button text class="-ml-3" @click="handleBack">
          <MkIcon name="icon_left_outlined" :size="18" />
        </el-button>
        <h4 class="max-w-[300px] truncate" :title="toolDetail?.name">
          {{ toolDetail?.name }}
        </h4>
        <span v-if="saveTime" class="shrink-0 text-sm text-N600"> 保存于 {{ datetimeFormat(saveTime) }} </span>
      </div>

      <div class="flex shrink-0 items-center gap-3">
        <WorkflowComponentMenu
          :current-resource="{ id: toolId, source: RESOURCE_TYPE.TOOL }"
          :workflow-mode="WorkflowMode.Tool"
          @dragstart="handleDragNode"
          @select="handleAddNode"
        />
        <el-button plain :loading="saving" :disabled="loading || saving" @click="handleSave"> 保存 </el-button>
      </div>
    </header>

    <WorkflowCanvas
      ref="workflowRef"
      class="min-h-0 flex-1"
      :current-resource="{ id: toolId, source: RESOURCE_TYPE.TOOL }"
      :loop-workflow-mode="WorkflowMode.ToolLoop"
      :workflow-mode="WorkflowMode.Tool"
    />
  </main>
</template>
