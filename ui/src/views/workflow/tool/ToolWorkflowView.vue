<script setup lang="ts">
import { nextTick, onMounted, provide, ref, useTemplateRef } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type LogicFlow from '@logicflow/core'
import type { Action } from 'element-plus'
import { cloneDeep } from 'lodash'
import ModelApi from '@/api/admin/workspace/model/model'
import ToolApi from '@/api/admin/workspace/tool/tool'
import ToolWorkflowApi from '@/api/admin/workspace/tool/workflow'
import type { DefaultModelSettingPayload, ToolItem, ToolWorkflowDetail } from '@/api/types'
import { MsgConfirm, MsgSuccess, MsgError } from '@/utils/message'
import WorkflowCanvas from '@/workflow-canvas/index.vue'
import { defaultToolNodes } from '@/workflow-canvas/config/node-mapping'
import { WorkflowMode } from '@/workflow-canvas/types'
import WorkflowViewLayout from '../components/WorkflowViewLayout.vue'
import DefaultModelSettingButton from '@/views/workflow/components/default-model-setting/DefaultModelSettingButton.vue'

defineOptions({ name: 'ToolWorkflowView' })

// 为画布节点中的 SelectModel 提供参数表单接口。
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

/* 工具工作流加载与保存 */
const toolDetail = ref<ToolItem>()
const loading = ref(false)
const saving = ref(false)
const publishing = ref(false)
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
  return ToolWorkflowApi.putToolWorkflow(toolId, { work_flow: graphData, default_model_setting: cloneDeep(defaultModelSetting.value) })
    .then((toolWorkflow) => {
      defaultModelSetting.value = cloneDeep(toolWorkflow.default_model_setting ?? {})
      saveTime.value = toolWorkflow.update_time || new Date()
      setSavedWorkflow(graphData)
      if (showMessage) MsgSuccess('保存成功')
      return toolWorkflow
    })
    .finally(() => {
      saving.value = false
    })
}

/* 应用默认模型设置：抽屉提交后暂存，保存失败时从详情回滚。 */
const defaultModelSetting = ref<DefaultModelSettingPayload>({})

function handleApplyDefaultModelToAll(graphData: LogicFlow.GraphData) {
  workflowRef.value?.renderGraphData(graphData)
}

function handleSaveDefaultModelSetting(settings: DefaultModelSettingPayload) {
  defaultModelSetting.value = cloneDeep(settings)
  return handleSave()
}

function handleSave() {
  saveToolWorkflow(undefined, true)
}

function handlePublish() {
  if (!workflowRef.value) return

  publishing.value = true
  workflowRef.value
    .validate()
    .then(() => saveToolWorkflow()) // 先保存未落库的画布改动
    .then(() => ToolWorkflowApi.putToolWorkflowPublish(toolId))
    .then(() => MsgSuccess('发布成功'))
    .catch(() => MsgError('发布失败'))
    .finally(() => {
      publishing.value = false
    })
}

function loadToolWorkflow() {
  loading.value = true
  return Promise.all([ToolApi.getToolDetail(toolId), ToolWorkflowApi.getToolWorkflow(toolId)])
    .then(([tool, toolWorkflow]) => {
      toolDetail.value = tool
      defaultModelSetting.value = cloneDeep(toolWorkflow.default_model_setting ?? {})
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
  MsgConfirm('提示', '当前工作流尚未保存，是否保存后退出？', {
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
      <DefaultModelSettingButton
        :model-value="defaultModelSetting"
        :model-api="ModelApi"
        :get-graph-data="getGraphData"
        :disabled="loading || saving || publishing"
        @save="handleSaveDefaultModelSetting"
        @apply-to-all="handleApplyDefaultModelToAll"
      />

      <el-button type="primary" :loading="publishing" :disabled="loading || saving || publishing" @click="handlePublish"> 发布 </el-button>
      <el-button plain :loading="saving" :disabled="loading || saving" @click="handleSave"> 保存 </el-button>
    </template>

    <WorkflowCanvas ref="workflowRef" class="min-h-0 flex-1" :default-model-settings="defaultModelSetting" :loop-workflow-mode="WorkflowMode.ToolLoop" :workflow-mode="WorkflowMode.Tool" />
  </WorkflowViewLayout>
</template>
