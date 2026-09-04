<script setup lang="ts">
import { nextTick, onMounted, provide, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { cloneDeep } from 'lodash'
import ModelApi from '@/api/admin/workspace/model/model'
import ToolApi from '@/api/admin/workspace/tool/tool'
import ToolWorkflowApi from '@/api/admin/workspace/tool/workflow'
import { RESOURCE_TYPE } from '@/api/enums'
import type { ToolItem, ToolWorkflowDetail } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultToolNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode, type ShapeItem } from '@/workflow-canvas/types'
import CreateNodeMenu from './components/CreateNodeMenu.vue'
import WorkflowViewLayout from './components/WorkflowViewLayout.vue'

defineOptions({ name: 'ToolWorkflowView' })

// 为画布节点中的 ModelSelect 提供参数表单接口。
provide('getModelParamsForm', ModelApi.getModelParamsForm)

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
  <WorkflowViewLayout :loading="loading" :title="toolDetail?.name" :save-time="saveTime" @back="handleBack">
    <template #actions>
      <CreateNodeMenu :workflow-mode="WorkflowMode.Tool" @select="handleAddNode" />
      <el-button plain :loading="saving" :disabled="loading || saving" @click="handleSave"> 保存 </el-button>
    </template>

    <WorkflowCanvas ref="workflowRef" class="min-h-0 flex-1" :loop-workflow-mode="WorkflowMode.ToolLoop" :workflow-mode="WorkflowMode.Tool" />
  </WorkflowViewLayout>
</template>
